class Group:
    def __init__(self):
        self.id = 0
        self.name = ''
        self.active = True
        self.creatorId = ''
        self.default = False


class CreateGroupRequest:
    def __init__(self):
        self.name = ''
        self.active = True
        self.default = False
        self.memberCount = 0
