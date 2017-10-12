'''Domo Python SDK Usage
- To run this file, clone the domo-python-sdk repository, plug in your ID and Secret, and execute "python3 run_examples.py"
- All created items are deleted at the end of their test
- If you encounter a 'Not Allowed' error, this is a permissions
issue. Please speak with your Domo Administrator.
- If you encounter a 'Forbidden' error, your OAuth client is likey
missing the scope required for that endpoint

Note that the Domo objects used in these examples are dictionaries
that prevent you from accidentally setting the wrong fields.
Dictionaries can be supplied instead, and the return objects are
dictionaries.
'''

import logging

import examples
from pydomo import Domo


CLIENT_ID = 'YOUR CLIENT ID'
CLIENT_SECRET = 'YOUR CLIENT SECRET'

# This can be changed to allow going through a proxy
# or to hit a mock for a test
API_HOST = 'api.domo.com'


def init_domo_client(client_id, client_secret, **kwargs):
    '''Create an API client on https://developer.domo.com
    Initialize the Domo SDK with your API client id/secret
    If you have multiple API clients you would like to use, simply
    initialize multiple Domo() instances
    Docs: https://developer.domo.com/docs/domo-apis/getting-started
    '''
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - '
                                  '%(message)s')
    ch.setFormatter(formatter)
    logging.getLogger().addHandler(ch)

    return Domo(client_id, client_secret, logger_name='foo',
                log_level=logging.INFO, **kwargs)


if __name__ == '__main__':
    domo = init_domo_client(CLIENT_ID, CLIENT_SECRET, api_host=API_HOST)
    examples.datasets(domo)
    examples.groups(domo)
    examples.pages(domo)
    examples.streams(domo)
    examples.users(domo)
