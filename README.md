# Python3 - Domo API SDK (pydomo)
[![License](https://img.shields.io/badge/license-MIT-blue.svg?style=flat)](http://www.opensource.org/licenses/MIT)

Current Release: 0.2.3

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
    - This SDK automates the use of Domo Streams so that uploads are always as fast as possible
    - Add Personalized Data Policies (PDPs) to DataSets (hide sensitive data from groups of users)
    - Docs: https://developer.domo.com/docs/domo-apis/data
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

### Available Functions
The functions in this package match most parts of the API documented at [developer.domo.com](https://developer.domo.com/) and follow a specific convention. Each set of functions is preceeded by the portion of the API it operates on. The following lists all the sets of functions available in this package. For further help, refer to the help function in Python.
* **Data sets** - This set of functions is designed to transfer data in and out of Domo.
	* **ds_get** - downloads data from Domo
	* **ds_create** - creates a new data set
	* **ds_update** - updates an existing data set, only data sets created by the API can be updated
	* **ds_meta** - downloads meta data regarding a single data set
	* **ds_list** - downloads a list of data sets in your Domo instance
	* **ds_delete** - deletes a data set (be careful)
	* **ds_query** - allows you to send a query to a data set, Domo will evaluate that query and sends the results back as a list or a tibble
	* **ds_rename** - renames an existing data set
* **Groups** - This set of functions modifies and creates groups.
	* **groups_add_users** - adds users to an existing group
	* **groups_create** - create a group
	* **groups_delete** - delete an existing group
	* **groups_list** - list all groups
	* **groups_remove_users** - remove users from a group
	* **groups_list_users** - list users in a group
* **Pages** - functions related to managing Domo pages
	* **page_update** - update a page
	* **page_list** - list all pages
	* **page_get_collections** - list all collections on a page
	* **page_get** - get information regarding a page
	* **page_create** - create a page
* **PDP** - functions to manage PDP
	* **pdp_update** - update an existing PDP policy
	* **pdp_list** - list all PDP policies
	* **pdp_enable** - toggle PDP on and off
	* **pdp_delete** - delete a PDP policy
	* **pdp_create** - create a PDP policy
* **Users** - functions to manage users
	* **users_delete** - delete a user
	* **users_update** - update a user
	* **users_list** - list all users
	* **users_get** - get a single user record
	* **users_add** - create a user (or users)