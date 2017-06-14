from pydomo.DomoAPIClient import DomoAPIClient

# """
#     Group Client
#     - Programmatically manage Domo User Groups
#     - Docs: https://developer.domo.com/docs/domo-apis/group-apis
# """


class RoleClient(DomoAPIClient):
    def __init__(self, transport, logger):
        super(RoleClient, self).__init__(transport, logger)
        self.urlBase = '/v1/roles/'
        self.description = "Role"
    #
    # """
    #     Create a Group
    # """
    # def create(self, group_request):
    #     return self._create(self.urlBase, group_request, {}, self.groupDesc)
    #
    """
        Get a Role
    """
    def get(self, role_id):
        return self._get(self._base(role_id), self.description)

    """
        List Roles
    """
    def list(self):
        return self._list(self.urlBase, {}, self.description)
    #
    # """
    #     Update a Group
    # """
    # def update(self, group_id, group_update):
    #     return self._update(self._base(group_id), HTTPMethod.PUT, requests.codes.ok, group_update, self.groupDesc)
    #
    # """
    #     Delete a Group
    # """
    # def delete(self, group_id):
    #     return self._delete(self._base(group_id), self.groupDesc)
    #
    # """
    #     Add a User to a Group
    # """
    # def add_user(self, group_id, user_id):
    #     url = self._base(group_id) + '/users/' + str(user_id)
    #     desc = "a User in a Group"
    #     return self._update(url, HTTPMethod.PUT, requests.codes.no_content, {}, desc)
    #
    # """
    #     List Users in a Group
    # """
    # def list_users(self, group_id):
    #     url = self._base(group_id) + '/users'
    #     desc = "a list of Users in a Group"
    #     return self._get(url, desc)
    #
    # """
    #     Remove a User to a Group
    # """
    # def remove_user(self, group_id, user_id):
    #     url = self._base(group_id) + '/users/' + str(user_id)
    #     desc = "a User in a Group"
    #     return self._delete(url, desc)
