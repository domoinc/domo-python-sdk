from pydomo.DomoAPIClient import DomoAPIClient
from pydomo.Transport import HTTPMethod
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
