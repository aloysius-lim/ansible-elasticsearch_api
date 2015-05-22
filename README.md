# Elasticsearch API

[![Build Status](https://travis-ci.org/abtpeople/ansible-elasticsearch_api.svg)](https://travis-ci.org/abtpeople/ansible-elasticsearch_api)

Ansible role and module to make API calls to Elasticsearch using the official [Python Elasticsearch Client](http://elasticsearch-py.readthedocs.org/en/master/).

It only needs to be installed on the host that the API calls are made from. For example, it can be installed on `localhost` and used to make calls to any Elasticsearch cluster.

It is recommended that all API calls are run only once, either by tagging them with `run_once: true`, or by running them from a single host. This ensures that Ansible does not make the same API call multiple times, which may cause unintended side effects.

### Features

* Access the full power and flexibility of the Elasticsearch APIs from Ansible playbooks
* Full support for all APIs, functions, and arguments in a simple and flexible syntax
* Install any available version of the Python Elasticsearch Client
* Choose not to install the client, if you are just making API calls

### Limitations

* API calls are not indempotent from Ansible's perspective. Every call is sent to Elasticsearch, whether or not changes are needed, and Elasticsearch handles it by its own rules. Elasticsearch may execute some API calls in an indempotent manner (e.g. not creating an index if it already exists), but it is impossible for Ansible to know whether a change has actually taken place.
* For that reason, all API calls are marked as `changed: true`, even if nothing has actually changed on the Elasticsearch cluster.

### Status

Operating System | Release | Status                                                                                                                                                                                                    |
---------------- | ------- | ------                                                                                                                                                                                                    |
centos           | 6       | [![Vagrant passed](https://img.shields.io/badge/vagrant-passed-brightgreen.svg?style=flat-square)](#) [![Docker passed](https://img.shields.io/badge/docker-passed-brightgreen.svg?style=flat-square)](#) |
centos           | 7       | [![Vagrant passed](https://img.shields.io/badge/vagrant-passed-brightgreen.svg?style=flat-square)](#) [![Docker passed](https://img.shields.io/badge/docker-passed-brightgreen.svg?style=flat-square)](#) |
debian           | wheezy  | [![Vagrant passed](https://img.shields.io/badge/vagrant-passed-brightgreen.svg?style=flat-square)](#) |
debian           | jessie  | [![Vagrant passed](https://img.shields.io/badge/vagrant-passed-brightgreen.svg?style=flat-square)](#) |
ubuntu           | precise | [![Vagrant passed](https://img.shields.io/badge/vagrant-passed-brightgreen.svg?style=flat-square)](#) |
ubuntu           | trusty  | [![Vagrant passed](https://img.shields.io/badge/vagrant-passed-brightgreen.svg?style=flat-square)](#) [![Docker passed](https://img.shields.io/badge/docker-passed-brightgreen.svg?style=flat-square)](#) |

## Requirements

Pip, to install the Python Elasticsearch Client. This role does not install pip; use your preferred role to install it on the host from which the API calls will be made.

## Role Variables

* `es_py_version`: The version of the Python Elasticsearch Client to install, e.g. "1.5.0" (default: unspecified).
* `es_py_state`: The state of the Python Elasticsearch Client package, one of `present`, `absent` or `latest` (default: `present`).
* `es_py_install`: Whether or not to install the Python Elasticsearch Client (default: `true`). Set this to `false` if the client has already been installed, and you are just making API calls.

## `elasticsearch_api` Module

The Elasticsearch API is exposed as an Ansible module called `elasticsearch_api`, which provides access to all API functions defined in the Python Elasticsearch Client. All API calls follow a standard format, including the Elasticsearch hosts to connect to, the API and function to call, and any connection or function arguments.

See the [API docs](http://elasticsearch-py.readthedocs.org/) for full API documentation.

### Options

#### `hosts`
The list of Elasticsearch hosts to connect to. [Reference](http://elasticsearch-py.readthedocs.org/en/master/api.html#elasticsearch)

*Required:* no

*Default:* `["localhost:9200"]`

#### `transport`
Name of transport class to establish connection with. [Reference](http://elasticsearch-py.readthedocs.org/en/master/transports.html)

*Required:* no

*Default:* `Urllib3HttpConnection `

*Choices:*

* `Connection`
* `Urllib3HttpConnection`
* `RequestsHttpConnection`
* `ThriftConnection`
* `MemcachedConnection`

#### `transport_args`
Dictionary of keyword arguments for the selected transport. See the API docs for the arguments that each transport type accepts.

*Required:* no

#### `api`
API to use, where the empty string refers to the main Elasticsearch API.

*Required:* no

*Default:* `""` (refers to the main Elasticsearch API)

*Choices:*

* `""` (empty string)
* `cat`
* `cluster`
* `indices`
* `nodes`
* `snapshot`

#### `function`
The API function to call.

*Required:* yes

#### `function_args`
A dictionary of keyword arguments for the specified function. See the API docs for the arguments tha each function accepts.

*Required:* no

## Example Playbook

```yaml
---
# Install specific version of the Python Elasticsearch Client
- hosts: 127.0.0.1
  roles:
    - { role: elasticsearch_api, es_py_version: "1.4.0" }

# Install latest version of the Python Elasticsearch Client
- hosts: 127.0.0.1
  roles:
    - { role: elasticsearch_api, es_py_state: "latest" }

# Remove the Python Elasticsearch Client
- hosts: 127.0.0.1
  roles:
    - { role: elasticsearch_api, es_py_state: "absent" }

# Make API calls
# Assume the Python package has already been installed
- hosts: 127.0.0.1
  roles:
    - { role: elasticsearch_api, es_py_install: false }
  tasks:
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
```

License
-------

MIT

Author Information
------------------

Aloysius Lim ([GitHub](https://github.com/aloysius-lim))

[About People](http://www.abtpeople.com/), a data science and design consultancy ([GitHub](https://github.com/abtpeople))
