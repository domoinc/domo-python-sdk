class CreateRoleRequest:
    def __init__(self):
        self.name = ''
        self.description = ''


class User:
    def __init__(self):
        self.id = ''
        self.email = ''
        self.role = ''
        self.name = ''
        self.createdAt = ''
        self.updatedAt = ''
        self.image = ''
