# Python3 - Domo API SDK (pydomo)
[![License](https://img.shields.io/badge/license-MIT-blue.svg?style=flat)](http://www.opensource.org/licenses/MIT)

Current Release: 0.3.0

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
Below are examples of how to use the SDK to perform a few common tasks. To run similar code on your system, do the following.
* Create an API Client on the [Domo Developer Portal](https://developer.domo.com/)
* Use your API Client id/secret to instantiate pydomo 'Domo()'
* Multiple API Clients can be used by instantiating multiple 'Domo()' clients
* Authentication with the Domo API is handled automatically by the SDK
* If you encounter a 'Not Allowed' error, this is a permissions issue. Please speak with your Domo Administrator.
```python
from pydomo import Domo

domo = Domo('client-id','secret',api_host='api.domo.com')

# Download a data set from Domo
car_data = domo.ds_get('2f09a073-54a4-4269-8c62-b776e67d59f0')

# Create a summary data set, taking the mean of dollars by make and model.
car_summary = car_data.groupby(['make','model']).agg({'dollars':'mean'}).reset_index()


# Create a new data set in Domo with the result, the return value is the data set id of the new data set.
car_ds = domo.ds_create(car_summary,'Python | Car Summary Data Set','Python | Generated during demo')

# Modify summary and then upload to the data set we already created. The SDK will update the data set schema automatically.
car_summary2 = car_data.groupby(['make','model'],as_index=False).agg({'dollars':'mean','email':'count'}).reset_index()
car_update = domo.ds_update(car_ds,car_summary2)


# Create PDP Policy
from pydomo.datasets import Policy, PolicyFilter, FilterOperator, PolicyType, Sorting

# Create policy filters
pdp_filter = PolicyFilter()
pdp_filter.column = 'make'  # The DataSet column to filter on
pdp_filter.operator = FilterOperator.EQUALS
pdp_filter.values = ['Honda']  # The DataSet row value to filter on

pdp_request = Policy()
pdp_request.name = 'Python | US East'
pdp_request.filters = [pdp_filter]
pdp_request.type = PolicyType.USER
pdp_request.users = []
pdp_request.groups = [1631291223]

domo.pdp_create(car_ds,pdp_request)


# Interact with groups
all_groups = domo.groups_list() # List all groups
all_users = domo.users_list() # List all users

# List all users in US South Division
domo.groups_list_users(328554991)

added_users = domo.groups_add_users(328554991,2063934980)
domo.groups_list_users(328554991)
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