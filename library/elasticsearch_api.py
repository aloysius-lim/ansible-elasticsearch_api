#!/usr/bin/python

DOCUMENTATION = '''
---
module: elasticsearch_api
short_description: Interface to Elasticsearch Python API
description:
  - Interface to C(elasticsearch-py), the official Elasticsearch API for Python
  - See U(http://elasticsearch-py.readthedocs.org/) for full API documentation
  - Run this module only on one host (can be the Ansible control machine or one of the ElasticSearch
    nodes). Do not run it on all ElasticSearch nodes, or all of them will try to execute the same
    thing.
version_added: 1.5.2
author: Aloysius Lim
requirements: [ elasticsearch-py 1.x.y ]
options:
  hosts:
    description:
      - List of Elasticsearch hosts to connect to.
      - See U(http://elasticsearch-py.readthedocs.org/en/master/api.html#elasticsearch)
    required: false
    default: '["localhost:9200"]'
  transport:
    description:
      - Name of transport class to establish connection with.
      - See U(http://elasticsearch-py.readthedocs.org/en/master/transports.html)
    required: false
    default: Urllib3HttpConnection
    choices:
      - Connection
      - Urllib3HttpConnection
      - RequestsHttpConnection
      - ThriftConnection
      - MemcachedConnection
  transport_args:
    description:
      - Dictionary of keyword arguments for the selected transport.
    required: false
  api:
    description:
      - API to use, where the empty string refers to the main Elasticsearch functions.
    default: ''
    choices: ['', cat, cluster, indices, nodes, snapshot]
  function:
    description:
      - API function to call.
    required: true
  function_args:
    description:
      - Dictionary of keyword arguments for the specified function.
    required: false
'''

EXAMPLES = '''
- name: Count number of documents on localhost
  elasticsearch_api:
    function: count

- name: Specify hosts to connect to, and connection settings
  elasticsearch_api:
    hosts: ['es1.mydomain.com', 'es2.mydomain.com']
    transport_args:
      use_ssl: true
      verify_certs: true
      maxsize: 5
    function: count

- name: Create an index with the specified settings and mapping
  elasticsearch_api:
    api: indices
    function: create
    function_args:
      index: my_index
      body: |
        {
          "settings": { "number_of_shards": 1 },
          "mappings": {
            "type1": {
              "properties": {
                "name": { "type": "string" },
                "date": { "type": "date" },
                "valid": { "type": "boolean" }
              }
            }
          }
        }

- name: Get status of indices with the indices API
  elasticsearch_api:
    api: indices
    function: status
'''

import elasticsearch
import elasticsearch.connection
import elasticsearch.helpers

def main():
    module = AnsibleModule(
        argument_spec=dict(
            hosts=dict(default=['localhost:9200'], type='list'),
            transport=dict(default='Urllib3HttpConnection', type='str',
                choices=['Connection', 'Urllib3HttpConnection', 'RequestsHttpConnection',
                'ThriftConnection', 'MemcachedConnection']),
            transport_args=dict(required=False, type='dict'),
            api=dict(default='', choices=['', 'cat', 'cluster', 'indices', 'nodes', 'snapshot', 'helpers']),
            function=dict(required=True, type='str'),
            function_args=dict(required=False, type='dict')
        ),
        supports_check_mode=False
    )

    hosts = module.params['hosts']
    transport = getattr(elasticsearch.connection, module.params['transport'])
    transport_args = module.params['transport_args'] or {}
    api = module.params['api']
    function = module.params['function']
    function_args = module.params['function_args'] or {}

    # Establish connection
    # Bug in elasticsearch-py where explicitly setting transport_class to 'Urllib3HttpConnection'
    # causes an error. So don't specify transport_class for the default.
    if transport.__name__ == 'Urllib3HttpConnection':
        es = elasticsearch.Elasticsearch(hosts, **transport_args)
    else:
        es = elasticsearch.Elasticsearch(hosts, transport_class=transport, **transport_args)

    try:
        # Call function
        if api == '':
            f = getattr(es, function)
        elif api == 'helpers':
            f = getattr(elasticsearch.helpers, function)
            function_args['client'] = es
        else:
            f = getattr(getattr(es, api), function)
        # Assume changed, since we can't detect changes.
        result = dict(changed=True)
        result['result'] = f(**function_args)
        module.exit_json(**result)
    except Exception, e:
        module.fail_json(msg=str(e))

# import module snippets
from ansible.module_utils.basic import *
main()
