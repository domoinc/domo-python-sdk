# PyDomo Changelog

### v0.3.0.6
October 21, 2022

Bug Fixes
* Now checks for invalid token before sending requests. If the token is invalid, the SDK now refreshes it automatically.

### v0.3.0.3
February 9, 2021

Bug Fixes
* ds_updated and ds_create did not upload the full dataframe when doing mult-part uploads
* pandas was not required in setup file

### v0.3.0.2
January 26, 2021

Updates
* Virtual user support added to PDP policy
* Pandas added to install.sh

### v0.3.0.1
January 21, 2021

Bug Fixes
* ds_query fixed to accept a data set id and a SQL query
* ds_delete now requires confirmation before deleting a data set
    * use prompt_before_delete=False to force delete
* group functions modified to match rdomo, prior to this release these functions did not work correctly
    * groups_add_users now adds multiple users at a time
    * groups_create now takes a group name and a list of users
    * groups_list now pages through all lists automatically
    * groups_list_users now pages through all users automatically
    * groups_remove_users now removes a list of users
    * groups_delete now removes all users from the group and then deletes the group 

### v0.3.0
January 8, 2021

The primary objective of this release is to make it easier to interact with Domo via Python and to sync functionality with the R SDK. The following changes have been made.
* Methods were added to the primary object so that the sub-objects don't need to be used.
* Method names sync'd with functions from the R SDK
* Method names follow a specific naming convention for ease of use
* Methods to download data from Domo now return a Pandas dataframe
* Methods to upload data to Domo now take a Pandas dataframe as an input
* Uploading data is now easier as interactions with the streams API are abstracted
* All methods prior to these updates are unchanged, existing code should continue to work w/o issue

### v0.2.3
- Apr 18, 2019
- Added GZIP support for Streams (Thank you @ldacey!)
- Added file support for Streams (Thank you @jonemi!)
- Added limit and offset support for listing Users in a Group

### v0.2.2.1
- Jan 11, 2018
- Circumventing issue in setup.py preventing installing via pip

### v0.2.2
- Jan 11, 2018
- Bug Fixes:
    - Fixed unicode error when uploading unicode data via stream client
    - Dataset client referenced log instead of logger

### v0.2.1
- Oct 16, 2017
- Improved csv downloading to disk, avoiding a potential python memory error

### v0.2.0
- Aug 17, 2017
- Added Pages:
    - List, create, update, and delete pages
    - List, create, update, and delete collections
- Improvements:
    - All endpoints now accept and return dictionaries. This will
      likely break existing code, but it allows for returned objects
      to be accepted as parameters.
    - Removed dependency on jsonpickle library
    - Eliminated an extra API call that was previously being used to
      check if access token is valid
    - Enable appending to datasets
- Bug Fixes:
    - Fixed unicode error when uploading/downloading unicode data

### v0.1.3
- Jul 6, 2017
- Improvements:
    - Better error descriptions, http request/response dumps on exception (requires requests_toolbelt)
- Bug Fixes:
    - Fixed Stream search (aldifahrezi)
    - Fixed DataSet export authentication renewal

### v0.1.2
- May 1, 2017
- Added functionality to the Group Client:
    - Add a User to a Group
    - List Users in a Group
    - Remove a User from a Group
- Added the "api host" as a parameter to the SDK initialization

### v0.1.1
- April 26, 2017
- Minor improvements for PyPI publishing
- Published the SDK to PyPI for easy Pip installation: `pip3 install pydomo`

### v0.1.0
- April 21, 2017
- Initial release
