from ..common import DomoObject


class CreateUserRequest(DomoObject):
    accepted_attrs = [
        'name',
        'email',
        'role'
    ]
