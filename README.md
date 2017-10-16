<div align="center">
  <img src="domo.png" width="400" height="400"/>
</div>

# Python3 - Domo API SDK (pydomo)
[![License](https://img.shields.io/badge/license-MIT-blue.svg?style=flat)](http://www.opensource.org/licenses/MIT)

Current Release: 0.2.1

### Notice - Python 3 Compatibility

* PyDomo is written for Python3, and is not compatible with Python2
* Execute scripts via 'python3', and updates via 'pip3'

### About

* The Domo API SDK is the simplest way to automate your Domo instance
* The SDK streamlines the API programming experience, allowing you to significantly reduce your written code
* This SDK was written for Python3, and is not compatible with Python2
* PyDomo has been published to [PyPI](https://pypi.org/project/pydomo/). The SDK can be easily installed via `pip3 install pydomo`, and can be updated via `pip3 install pydomo --upgrade`

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
- Page Management
    - Create, update, and delete pages
    - Docs: https://developer.domo.com/docs/page-api-reference/page

### Setup
* Install Python3: https://www.python.org/downloads/
    * Linux: 'apt-get install python3'
    * MacOS: 'brew install python3'
    * Windows: direct download, or use Bash on Windows 10
* Install PyDomo and its dependencies via `pip3 install pydomo`

### Updates
* Update your PyDomo package via `pip3 install pydomo --upgrade`
* View the [changelog](CHANGELOG.md)

### Usage
* See [examples.py](run_examples.py) for full usage
* To run this file, copy/paste its contents, enter your ID and Secret (https://developer.domo.com/manage-clients), and execute "python3 run_examples.py"
* Create an API Client on the [Domo Developer Portal](https://developer.domo.com/)
* Use your API Client id/secret to instantiate pydomo 'Domo()'
* Multiple API Clients can be used by instantiating multiple 'Domo()' clients
* Authentication with the Domo API is handled automatically by the SDK
* If you encounter a 'Not Allowed' error, this is a permissions issue. Please speak with your Domo Administrator.
```python
import logging
from pydomo import Domo

# Build an SDK configuration
client_id = 'MY_CLIENT_ID'
client_secret = 'MY_CLIENT_SECRET'
api_host = 'api.domo.com'

# Configure the logger
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logging.getLogger().addHandler(handler)

# Create an instance of the SDK Client
domo = Domo(client_id, client_secret, logger_name='foo', log_level=logging.INFO, api_host=api_host)

# Manage DataSets
domo.datasets.create()

# Manage Streams
domo.streams.create()

# Manage Users
domo.users.create()

# Manage User Groups
domo.groups.create()

# Manage Pages
domo.pages.create()
```