from random import randint

from pydomo.users import CreateUserRequest


def users(domo):
    '''User Docs: https://developer.domo.com/docs/domo-apis/users
    '''
    domo.logger.info("\n**** Domo API - User Examples ****\n")

    # Build a User
    user_request = CreateUserRequest()
    user_request.name = 'Leonhard Euler'
    user_request.email = 'leonhard.euler{}@domo.com'.format(randint(0, 10000))
    user_request.role = 'Privileged'
    send_invite = False

    # Create a User
    user = domo.users.create(user_request, send_invite)
    domo.logger.info("Created User '{}'".format(user['name']))

    # Get a User
    user = domo.users.get(user['id'])
    domo.logger.info("Retrieved User '" + user['name'] + "'")

    # List Users
    user_list = domo.users.list(10, 0)
    domo.logger.info("Retrieved a list containing {} User(s)".format(
                                                               len(user_list)))

    # Update a User
    user_update = CreateUserRequest()
    user_update.name = 'Leo Euler'
    user_update.email = 'leo.euler{}@domo.com'.format(randint(0, 10000))
    user_update.role = 'Privileged'
    user = domo.users.update(user['id'], user_update)
    domo.logger.info("Updated User '{}': {}".format(user['name'],
                                                    user['email']))

    # Delete a User
    domo.users.delete(user['id'])
    domo.logger.info("Deleted User '{}'".format(user['name']))
