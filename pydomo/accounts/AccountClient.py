import requests

from pydomo.DomoAPIClient import DomoAPIClient
from pydomo.Transport import HTTPMethod

ACCOUNT_DESC = "Account"
ACCOUNT_TYPE_DESC = "Account Type"
URL_BASE = '/v1/accounts'

ACCOUNT_CREATION_KWARGS = [
    'name',
    'type',
]

account_UPDATE_KWARGS = [
    'id',
    'name',
    'parentId',
    'ownerId',
    'locked',
    'collectionIds',
    'cardIds',
    'visibility'
]



class AccountClient(DomoAPIClient):
    """
        Account
        - Programmatically manage Domo Accounts
        - Docs: https://developer.domo.com/docs/accounts-api-reference/account-api-reference
    """

    
    def list(self, per_account=50, offset=0, limit=0):
        """List Accounts.
        Returns a generator that will call the API multiple times
        If limit is supplied and non-zero, returns up to limit accounts

        >>> list(domo.account.list())
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