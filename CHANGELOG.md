# PyDomo Changelog
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
