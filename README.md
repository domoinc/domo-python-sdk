# domo-python-sdk (pydomo)
[![License](https://img.shields.io/badge/license-MIT-blue.svg?style=flat)](http://www.opensource.org/licenses/MIT)

### About

The official Domo Python3 SDK (PyDomo)
* The Domo API SDK is the simplest way to automate your Domo instance
* The SDK streamlines the API programming experience, allowing you to significantly reduce your written code
* This has not yet been tested with Python2
* PyDomo has been published to [PyPI](https://pypi.python.org/pypi/pydomo), and can be installed via `pip3 install pydomo requests jsonpickle`

### Features:
- DataSet and Personalized Data Policy (PDP) Management
    - Use DataSets for fairly static data sources that only require occasional updates via data replacement
    - Add Personalized Data Policies (PDPs) to DataSets (hide sensitive data from groups of users)
    - Docs: https://developer.domo.com/docs/domo-apis/data
- Stream Management
    - A Domo Stream is a specialized upload pipeline pointing to a single Domo DataSet
    - Use Streams for massive, constantly changing, or rapidly growing data sources
    - Streams support accelerated uploading via parallel data uploads
    - Docs: https://developer.domo.com/docs/domo-apis/stream-apis
- User Management
    - Create, update, and remove users
    - Major use case: LDAP/Active Directory synchronization
    - Docs: https://developer.domo.com/docs/domo-apis/users
- Group Management
    - Create, update, and remove groups of users
    - Docs: https://developer.domo.com/docs/domo-apis/group-apis

### Setup
* Install Python3: https://www.python.org/downloads/
    * Linux: 'apt-get install python3'
    * MacOS: 'brew install python3'
    * Windows: direct download, or use Bash on Windows 10
* Install PyDomo and its dependencies via `pip3 install pydomo requests jsonpickle`

### Usage
* See 'examples.py' for full usage
* Create an API Client on the [Domo Developer Portal](https://developer.domo.com/)
* Use your API Client id/secret to instantiate pydomo 'Domo()'
* Multiple API Clients can be used by instantiating multiple 'Domo()' clients
* Authentication with the Domo API is handled automatically by the SDK
* If you encounter a 'Not Allowed' error, this is a permissions issue. Please speak with your Domo Administrator.
```python
import logging
from pydomo import Domo
client_id = 'MY_CLIENT_ID'
client_secret = 'MY_CLIENT_SECRET'
logger_name = 'foo'
logger_level = logging.INFO
domo = Domo(client_id, client_secret, logger_name, logger_level)

# Manage DataSets
domo.datasets.create()

# Manage Streams
domo.streams.create()

# Manage Users
domo.users.create()

# Manage User Groups
domo.groups.create()
```
