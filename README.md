# domo-python-sdk (pydomo)
[![License](https://img.shields.io/badge/license-MIT-blue.svg?style=flat)](http://www.opensource.org/licenses/MIT)

### About

The official Domo Python3 SDK (PyDomo)
* This has not yet been tested with Python2
* PyDomo has been published to PyPI, and can be installed via `pip3 install pydomo requests jsonpickle`

### Features:
* DataSet Management: https://developer.domo.com/docs/domo-apis/data
* Stream Management: https://developer.domo.com/docs/domo-apis/stream-apis
* User Management: https://developer.domo.com/docs/domo-apis/users
* User Group Management: https://developer.domo.com/docs/domo-apis/group-apis

### Setup
* Install Python3: https://www.python.org/downloads/
    * Linux: 'apt-get install python3'
    * MacOS: 'brew install python3'
    * Windows: direct download, or use Bash on Windows 10
* Install PyDomo and its dependencies via `pip3 install pydomo requests jsonpickle`

### Usage
* See 'examples.py' for full usage
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
domo.datasets.create()
domo.streams.create()
domo.users.create()
domo.groups.create()
```
