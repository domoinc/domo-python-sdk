from ..common import DomoObject


class CreateGroupRequest(DomoObject):
    accepted_attrs = [
        'name',
        'active',
        'default',
        'memberCount'
    ]
