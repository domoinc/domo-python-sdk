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

        >>> account = { 'name': 'DataSet Copy Test', 'valid': True, 'type': {'id': 'domo-csv', 'properties': {}}}
        >>> new_account = domo.accounts.create(**account)
        >>> print(new_account)
        {'name': 'DataSet Copy Test', 'valid': True, 'type': {'id': 'domo-csv', 'properties': {}}}


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
        {'id': '40', 'name': 'DataSet Copy Test', 'valid': True, 'type': {'id': 'domo-csv', 'properties': {}}}

        :Parameters:
          - `account_id`: ID of the account to get (str)

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
        [{'id': '40', 'name': 'DataSet Copy Test', ...},
        {'id': '41', 'name': 'DataSet Copy Test2', ...}]

        :Parameters:
        - `per_page`:   results per page. Default 50 (int)
        - `offset`:     offset if you need to paginate results. Default 0 (int)
        - `limit`:      max ouput to return. If 0 then return all results on page. Default 0 (int)
            

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
        {'id': '40', 'name': 'DataSet Copy Test', 'valid': True, 'type': {'id': 'domo-csv', 'properties': {}}}
        updatedAccount = {'name': 'DataSet Copy Test2, 'valid': True, 'type': {'id': 'domo-csv', 'properties': {}}}
        >>> domo.accounts.update(account_id, **updatedAccount)
        >>> print(domo.accounts.get(account_id))
        {'id': '40', 'name': 'DataSet Copy Test2, 'valid': True, 'type': {'id': 'domo-csv', 'properties': {}}}


        :Parameters:
          - `account_id`: ID of the account to update.
          - `kwargs`: New account object
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
