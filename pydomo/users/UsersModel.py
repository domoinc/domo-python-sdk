class CreateUserRequest:
    def __init__(self):
        self.name = ''
        self.email = ''
        self.role = ''


class User:
    def __init__(self):
        self.id = ''
        self.email = ''
        self.role = ''
        self.name = ''
        self.createdAt = ''
        self.updatedAt = ''
        self.image = ''
