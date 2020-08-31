import requests

from pydomo.DomoAPIClient import DomoAPIClient
from pydomo.Transport import HTTPMethod

ACCOUNT_DESC = "Account"
URL_BASE = '/v1/accounts'

ACCOUNT_CREATION_KWARGS = [
    'name',
    'type',
    'valid'
]


class AccountClient(DomoAPIClient):
    """
        accounts
        - Programmatically manage Domo accounts
        - Docs: https://developer.domo.com/docs/accounts-api-reference/account-api-reference
    """

    def create(self, **kwargs):
        """Create a new account.

        >>> account = {
              "name": "Leonhard Euler's XYZ Account",
              'valid': True
              "type": {
                  "id": "xyz",
                  "properties": {
                      "password": "cyclops",
                      "authenticateBy": "PASSWORD",
                      "url": "https://mathematicians.xyz.com",
                      "username": "leonhard.euler@mathematicians.com"
                  }
              }
          }
        >>> new_account = domo.accounts.create(**account)
        >>> print(new_account)


        :Returns:
          - A dict representing the account
        """

        self._validate_params(kwargs, ACCOUNT_CREATION_KWARGS)

        account_request = kwargs
        print(account_request)
        return self._create(URL_BASE, account_request, {}, ACCOUNT_DESC)

    def get(self, account_id):
        """Get a account.

        >>> account = domo.accounts.get(account_id)
        >>> print(account)
        {'id': 123456789, 'parentId': 0, 'name': 'My account',
        'locked': False, 'ownerId': 12345, 'cardIds': [],
        'visibility': {'userIds': 12345}}

        :Parameters:
          - `account_id`: ID of the account to get

        :returns:
          - A dict representing the account
        """
        url = '{base}/{account_id}'.format(base=URL_BASE, account_id=account_id)
        return self._get(url, ACCOUNT_DESC)

    def list(self, per_account=50, offset=0, limit=0):
        """List accounts.
        Returns a generator that will call the API multiple times
        If limit is supplied and non-zero, returns up to limit accounts

        >>> list(domo.accounts.list())
        [{'id': 123456789, 'name': 'My account', 'children': []}, ...]

        :returns:
          - A list of dicts (with nesting possible)
        """
        # API uses pagination with a max of 50 per account
        if per_account not in range(1, 51):
            raise ValueError('per_account must be between 1 and 50 (inclusive)')
        # Don't pull 50 values if user requests 10
        if limit:
            per_account = min(per_account, limit)

        params = {
            'limit': per_account,
            'offset': offset,
        }
        account_count = 0

        accounts = self._list(URL_BASE, params, ACCOUNT_DESC)
        while accounts:
            for account in accounts:
                yield account
                account_count += 1
                if limit and account_count >= limit:
                    return

            params['offset'] += per_account
            if limit and params['offset'] + per_account > limit:
                # Don't need to pull more than the limit
                params['limit'] = limit - params['offset']
            accounts = self._list(URL_BASE, params, ACCOUNT_DESC)

    def update(self, account_id=None, **kwargs):
        """Update a account.

        >>> print(domo.accounts.get(account_id))
        {'id': 123456789, 'parentId': 0, 'name': 'My account',
        'locked': False, 'ownerId': 12345, 'cardIds': [],
        'visibility': {'userIds': 12345}}
        >>> domo.accounts.update(account_id, locked=True,
                              cardIds=[54321, 13579])
        >>> print(domo.accounts.get(account_id))
        {'id': 123456789, 'parentId': 0, 'name': 'My account',
        'locked': True, 'ownerId': 12345, 'cardIds': [54321, 13579],
        'visibility': {'userIds': 12345}}


        :Parameters:
          - `account_id`: ID of the account to update. Can also be provided
            by supplying `id` to **kwargs. This allows for calling get,
            updating the returned object, then passing it to update.
          - `name`: (optional) rename the account
          - `parentId`: (optional) turn account into subaccount, or subaccount
            into top-level account if parentId is present and falsey
          - `ownerId`: (optional) change owner of the account
          - `locked`: (optional) lock or unlock the account
          - `collectionIds`: (optional) reorder collections on account
          - `cardIds`: (optional) specify which cards to have on account
          - `visibility`: (optional) change who can see the account
        """

        url = '{base}/{account_id}'.format(base=URL_BASE, account_id=account_id)
        return self._update(url,
                            HTTPMethod.PATCH,
                            requests.codes.accepted,
                            kwargs,
                            ACCOUNT_DESC)

    def delete(self, account_id):
        """Delete a account.

        :Parameters:
          - `account_id`: ID of the account to delete
        """
        url = '{base}/{account_id}'.format(base=URL_BASE, account_id=account_id)
        return self._delete(url, ACCOUNT_DESC)
