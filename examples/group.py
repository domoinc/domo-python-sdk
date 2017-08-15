from random import randint
from pydomo.groups import CreateGroupRequest


def groups(domo):
    '''Group Docs:
    https://developer.domo.com/docs/domo-apis/group-apis
    '''
    domo.logger.info("\n**** Domo API - Group Examples ****\n")
    groups = self.domo.groups

    # Build a Group
    group_request = CreateGroupRequest()
    group_request.name = 'Groupy Group {}'.format(randint(0, 10000))
    group_request.active = True
    group_request.default = False

    # Create a Group
    group = groups.create(group_request)
    domo.logger.info("Created Group '{}'".format(group['name']))

    # Get a Group
    group = groups.get(group['id'])
    domo.logger.info("Retrieved Group '{}'".format(group['name']))

    # List Groups
    group_list = groups.list(10, 0)
    domo.logger.info("Retrieved a list containing {} Group(s)".format(
                                                          len(group_list)))

    # Update a Group
    group_update = CreateGroupRequest()
    group_update.name = 'Groupy Group {}'.format(randint(0, 10000))
    group_update.active = False
    group_update.default = False
    group = groups.update(group['id'], group_update)
    domo.logger.info("Updated Group '{}'".format(group['name']))

    # Add a User to a Group
    user_list = self.domo.users.list(10, 0)
    user = user_list[0]
    groups.add_user(group['id'], user['id'])
    domo.logger.info("Added User {} to Group {}".format(user['id'],
                                                        group['id']))

    # List Users in a Group
    user_list = groups.list_users(group['id'])
    domo.logger.info("Retrieved a User list from a Group containing {} User(s)"
                     .format(len(user_list)))

    # Remove a User from a Group
    groups.remove_user(group['id'], user['id'])
    domo.logger.info("Removed User {} from Group {}".format(user['id'],
                                                            group['id']))

    # Delete a Group
    groups.delete(group['id'])
    domo.logger.info("Deleted group '{}'".format(group['name']))
