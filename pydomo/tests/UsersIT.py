from pydomo.users import CreateUserRequest
from random import randint


class UserTestSuite:
    def __init__(self, domo):
        self.domo = domo
        self.logger = self.domo.logger
        self.shouldHaveFailed = "!!!!!!!!!!!!!!!!!!!!!!!! THIS TEST SHOULD HAVE FAILED !!!!!!!!!!!!!!!!!!!!!!!!"

    def run_all(self):
        user = self.create_successful()

        # Create
        # self.create_bad_email()
        # self.create_duplicate_email()
        # self.create_nonexistent_role()

        # Get
        #self.get_successful(user)
        #self.get_bad_id()

        # List
        # self.list_successful(user)
        # self.list_bad_limit()
        # self.list_bad_offset()
        # self.list_massive_limit()
        # self.list_massive_offset()

        # Update
        self.update_successful(user)
        #self.update_load_test(user)
        self.update_single_property_obj(user)

    @staticmethod
    def build_user_request():
        user_request = CreateUserRequest()
        user_request.name = 'Leonhard Euler'
        user_request.email = 'leonhard.euler' + str(randint(0, 10000)) + '@domo.com'
        user_request.role = 'Privileged'
        return user_request

    def create_successful(self):
        self.logger.info("\n\n**** Creating a basic user ****\n")

        # Build a User
        name = 'Leonhard Euler'
        email = 'leonhard.euler' + str(randint(0, 10000)) + '@domo.com'
        role = 'Privileged'
        user_request = CreateUserRequest()
        user_request.name = name
        user_request.email = email
        user_request.role = role
        send_invite = True

        # Create the User
        user = self.domo.users.create(user_request, send_invite)

        # Verify the User
        assert user.name == name
        assert user.email == email
        assert user.role == role

        return user

    def create_bad_email(self):
        self.logger.info("\n\n**** Creating a user with a bad email address ****\n")
        user_request = self.build_user_request()
        user_request.email = 'leonhard.euler' + str(randint(0, 10000))  # bad email address
        send_invite = True


        # Create the User
        has_failed = False
        try:
            self.domo.users.create(user_request, send_invite)
        except Exception as e:
            has_failed = True
            self.logger.error(str(e))
        if not has_failed:
            self.logger.error(self.shouldHaveFailed)
            #    raise Exception("This test passed when it was expected to fail")

    def create_duplicate_email(self):
        self.logger.info("\n\n**** Creating a user with a duplicate email address ****\n")
        has_failed = False
        # Build a User
        user_request = self.build_user_request()
        send_invite = True

        # Create the User
        self.domo.users.create(user_request, send_invite)

        # Create the User again
        try:
            self.domo.users.create(user_request, send_invite)
        except Exception as e:
            has_failed = True
            self.logger.error(str(e))
            assert 'EMAIL_DUPLICATE' in str(e), "Email duplication response not found!"
        if not has_failed:
            raise Exception(self.shouldHaveFailed)

    def create_nonexistent_role(self):
        self.logger.info("\n\n**** Creating a user with a non-existent role ****\n")
        has_failed = False
        # Build a User
        user_request = self.build_user_request()
        user_request.role = 'Cheez'
        send_invite = True

        # Create the User
        try:
            self.domo.users.create(user_request, send_invite)
        except Exception as e:
            has_failed = True
            self.logger.error(str(e))
            assert 'No enum constant' in str(e), "Enum description not found!"
        if not has_failed:
            raise Exception(self.shouldHaveFailed)

    def get_successful(self, user):
        self.logger.info("\n\n**** Getting a User ****\n")
        retrieved = self.domo.users.get(user.id)

        # Verify the User
        assert retrieved.name == user.name
        assert retrieved.email == user.email
        assert retrieved.role == user.role

    def get_bad_id(self):
        self.logger.info("\n\n**** Getting a user with a bad id ****\n")
        has_failed = False
        try:
            user_id = -1
            self.domo.users.get(user_id)
        except Exception as e:
            has_failed = True
            self.logger.error(str(e))
            assert '404' in str(e), "Error 404 not found!"
        if not has_failed:
            raise Exception(self.shouldHaveFailed)

    def list_successful(self, user):
        self.logger.info("\n\n**** Listing users ****\n")
        limit = 5000
        offset = 0
        user_list = self.domo.users.list(limit, offset)

        assert len(user_list) >= 1, "The user list is empty!!"

        has_my_user = False
        for u in user_list:
            if u.id == user.id:
                has_my_user = True

        assert has_my_user is True, "The recently created user is missing!"

    def list_bad_limit(self):
        self.logger.info("\n\n**** Listing users with a bad limit ****\n")
        has_failed = False
        try:
            limit = -1
            offset = 0
            self.domo.users.list(limit, offset)
        except Exception as e:
            has_failed = True
            self.logger.error(str(e))
            assert '400' in str(e), "Error 400 not found!"
        if not has_failed:
            raise Exception(self.shouldHaveFailed)

    def list_bad_offset(self):
        self.logger.info("\n\n**** Listing users with a bad offset ****\n")
        has_failed = False
        try:
            limit = 50
            offset = -1
            self.domo.users.list(limit, offset)
        except Exception as e:
            has_failed = True
            self.logger.error(str(e))
            assert '400' in str(e), "Error 400 not found!"
        if not has_failed:
            raise Exception(self.shouldHaveFailed)

    def list_massive_limit(self):
        self.logger.info("\n\n**** Listing users with a massive limit ****\n")
        has_failed = False
        try:
            limit = 5000000
            offset = 0
            self.domo.users.list(limit, offset)
        except Exception as e:
            has_failed = True
            self.logger.error(str(e))
            assert '400' in str(e), "Error 400 not found!"
        if not has_failed:
            self.logger.error(self.shouldHaveFailed)
            #    raise Exception(self.shouldHaveFailed)

    def list_massive_offset(self):
        self.logger.info("\n\n**** Listing users with a massive offset ****\n")
        has_failed = False
        try:
            limit = 50
            offset = 5000000
            self.domo.users.list(limit, offset)
        except Exception as e:
            has_failed = True
            self.logger.error(str(e))
            assert '400' in str(e), "Error 400 not found!"
        if not has_failed:
            self.logger.error(self.shouldHaveFailed)
        #    raise Exception(self.shouldHaveFailed)

    def update_successful(self, original_user):
        self.logger.info("\n\n**** Updating a User ****\n")

        user_update = CreateUserRequest()
        user_update.name = 'Leo Euler'
        user_update.email = 'leo.euler' + str(randint(0, 10000)) + '@domo.com'
        user_update.role = 'Admin'
        updated_user = self.domo.users.update(original_user.id, user_update)

        assert updated_user.name != original_user.name
        assert updated_user.email != original_user.email
        assert updated_user.role != original_user.role

    def update_single_property_obj(self, original_user):
        self.logger.info("\n\n**** Updating a User with a single property object ****\n")

        user_update = {
            'email': 'leo.euler' + str(randint(0, 10000)) + '@domo.com',
            'name': 'Leonard Euler III',
            'role': 'Admin'
        }
        updated_user = self.domo.users.update(original_user.id, user_update)

        assert updated_user.email != original_user.email

    def update_load_test(self, user):
        self.logger.info("\n\n**** Updating a User 50 times in quick succession ****\n")
        try:
            for i in range(0, 49):
                self.update_successful(user)
        except Exception as e:
            self.logger.error(str(e))



        # def create_custom_role(self):
    #     self.logger.info("\n**** Domo API - User Examples ****\n")
    #     users = self.domo.users
    #
    #     # Build a custom role User
    #     user_request = CreateUserRequest()
    #     user_request.name = 'Leonhard Euler'
    #     user_request.email = 'leonhard.euler' + str(randint(0, 10000)) + '@domo.com'
    #     user_request.role = 'Bacon'
    #     user_request.roleId = 6
    #     send_invite = False
    #
    #     # Create the custom role User
    #     user = users.create(user_request, send_invite)
    #     self.logger.info("Created User '" + user.name + "'")
    #
    #     # user_list = users.list(50,0)
    #     # self.logger.info("User List: " + str(user_list))

    def users(self):
        # User Docs: https://developer.domo.com/docs/domo-apis/users
        self.logger.info("\n**** Domo API - User Examples ****\n")
        users = self.domo.users

        # Build a User
        user_request = CreateUserRequest()
        user_request.name = 'Leonhard Euler'
        user_request.email = 'leonhard.euler' + str(randint(0, 10000)) + '@domo.com'
        user_request.role = 'Privileged'
        send_invite = False

        # Create a User
        user = users.create(user_request, send_invite)
        self.logger.info("Created User '" + user.name + "'")

        # Get a User
        user = users.get(user.id)
        self.logger.info("Retrieved User '" + user.name + "'")

        # List Users
        user_list = users.list()
        self.logger.info("Retrieved a list containing " + str(len(user_list)) + " User(s)")

        # Update a User
        user_update = CreateUserRequest()
        user_update.name = 'Leo Euler'
        user_update.email = 'leo.euler' + str(randint(0, 10000)) + '@domo.com'
        user_update.role = 'Privileged'
        user = users.update(user.id, user_update)
        self.logger.info("Updated User '" + user.name + "' : " + user.email)

        # Delete a User
        users.delete(user.id)
        self.logger.info("Deleted User '" + user.name + "'")