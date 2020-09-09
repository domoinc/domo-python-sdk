from pydomo.DomoAPIClient import DomoAPIClient
from pydomo.Transport import HTTPMethod
import pandas as pd
import requests

"""
    User Client
    - Programmatically manage Domo users
    - Docs: https://developer.domo.com/docs/domo-apis/users
"""


class UserClient(DomoAPIClient):
    def __init__(self, transport, logger):
        super(UserClient, self).__init__(transport, logger)
        self.urlBase = '/v1/users/'
        self.userDesc = "User"

    """
        Create a User
    """
    def create(self, user_request, send_invite):
        params = {'sendInvite': str(send_invite)}
        return self._create(self.urlBase, user_request, params, self.userDesc)

    """
        Get a User
    """
    def get(self, user_id):
        return self._get(self._base(user_id), self.userDesc)

    """
        List Users
    """
    def list(self, limit, offset):
        params = {
            'limit': str(limit),
            'offset': str(offset),
        }
        return self._list(self.urlBase, params, self.userDesc)

    """
        Update a User
    """
    def update(self, user_id, user_update):
        return self._update(self._base(user_id), HTTPMethod.PUT, requests.codes.ok, user_update, self.userDesc)

    """
        Delete a User
    """
    def delete(self, user_id):
        return self._delete(self._base(user_id), self.userDesc)

    """
        List all users
    """
    def list_all(self, df_output=True,batch_size=500):
        i = 0
        n_ret = 1
        while n_ret > 0:
            ll = self.list(batch_size,batch_size*i)
            if( i == 0 ):
                all = ll
            else:
                all.extend(ll)
            i = i + 1
            n_ret = ll.__len__()

        out = all

        if( df_output ):
            out = pd.DataFrame(all)

        return(out)
