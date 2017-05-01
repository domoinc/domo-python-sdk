from pydomo import Domo
from pydomo.datasets import DataSetRequest, Schema, Column, ColumnType, Policy, PolicyFilter, FilterOperator, PolicyType
from pydomo.groups import CreateGroupRequest
from pydomo.streams import UpdateMethod, CreateStreamRequest
from pydomo.users import CreateUserRequest
from random import randint
import logging

"""
    Domo Python SDK Usage
    - Execute these examples/tests via 'python3 examples.py'
    - All created items are deleted at the end of their test
    - If you encounter a 'Not Allowed' error, this is a permissions issue. Please speak with your Domo Administrator.
"""


class DomoSDKExamples:
    def __init__(self):
        # Docs: https://developer.domo.com/docs/domo-apis/getting-started
        # Create an API client on https://developer.domo.com
        # Initialize the Domo SDK with your API client id/secret
        # If you have multiple API clients you would like to use, simply initialize multiple Domo() instances
        client_id = 'MY_CLIENT_ID'
        client_secret = 'MY_CLIENT_SECRET'
        api_host = 'api.domo.com'
        use_https = True
        logger_name = 'foo'
        logger_level = logging.INFO
        self.domo = Domo(client_id, client_secret, api_host, use_https, logger_name, logger_level)
        self.logger = self.domo.logger

    # DataSets are useful for data sources that only require occasional replacement
    def datasets(self):
        # DataSet Docs: https://developer.domo.com/docs/data-apis/data
        self.logger.info("\n**** Domo API - DataSet Examples ****\n")
        datasets = self.domo.datasets

        # Define a DataSet Schema
        dsr = DataSetRequest()
        dsr.name = 'Leonhard Euler Party'
        dsr.description = 'Mathematician Guest List'
        dsr.schema = Schema([Column(ColumnType.STRING, 'Friend')])

        # Create a DataSet with the given Schema
        dataset = datasets.create(dsr)
        self.logger.info("Created DataSet " + str(dataset.id))

        # Get a DataSets's metadata
        retrieved_dataset = datasets.get(dataset.id)
        self.logger.info("Retrieved DataSet " + str(retrieved_dataset.id))

        # List DataSets
        sort_by = 'name'
        limit = 50  # The API max limit is 50; use offset pagination to retrieve more DataSets
        offset = 0
        dataset_list = datasets.list(sort_by, limit, offset)
        self.logger.info("Retrieved a list containing " + str(len(dataset_list)) + " DataSet(s)")

        # Update a DataSets's metadata
        update = DataSetRequest()
        update.name = 'Leonhard Euler Party - Update'
        update.description = 'Mathematician Guest List - Update'
        update.schema = Schema([Column(ColumnType.STRING, 'Friend'), Column(ColumnType.STRING, 'Attending')])
        updated_dataset = datasets.update(dataset.id, update)
        self.logger.info("Updated DataSet " + str(updated_dataset.id) + " : " + updated_dataset.name)

        # Import Data from a string
        csv_upload = "\"Pythagoras\",\"FALSE\"\n\"Alan Turing\",\"TRUE\"\n\"George Boole\",\"TRUE\""
        datasets.data_import(dataset.id, csv_upload)
        self.logger.info("Uploaded data to DataSet " + str(dataset.id))

        # Export Data to a string
        include_csv_header = True
        csv_download = datasets.data_export(dataset.id, include_csv_header)
        self.logger.info("Downloaded data as a string from DataSet " + str(dataset.id) + ":\n" + str(csv_download))

        # Export Data to a file (also returns the readable/writable file object)
        csv_file_path = './math.csv'
        include_csv_header = True
        csv_file = datasets.data_export_to_file(dataset.id, csv_file_path, include_csv_header)
        csv_file.close()
        self.logger.info("Downloaded data as a file from DataSet " + str(dataset.id))

        # Import Data from a file
        csv_file_path = './math.csv'
        datasets.data_import_from_file(dataset.id, csv_file_path)
        self.logger.info("Uploaded data from a file to DataSet " + str(dataset.id))

        # Personalized Data Policies (PDPs)

        # Build a Policy Filter (hide sensitive columns/values from users)
        pdp_filter = PolicyFilter()
        pdp_filter.column = 'Attending'  # The DataSet column to filter on
        pdp_filter.operator = FilterOperator.EQUALS
        pdp_filter.values = ['TRUE']  # The DataSet row value to filter on

        # Build the Personalized Data Policy (PDP)
        pdp_request = Policy()
        pdp_request.name = 'Only show friends attending the party'
        pdp_request.filters = [pdp_filter]  # A single PDP can contain multiple filters
        pdp_request.type = PolicyType.USER
        pdp_request.users = [998, 999]  # The affected user ids (restricted access by filter)
        pdp_request.groups = [99, 100]  # The affected group ids (restricted access by filter)

        # Create the PDP
        pdp = datasets.create_pdp(dataset.id, pdp_request)
        self.logger.info("Created a Personalized Data Policy (PDP): " + pdp.name + ", id: " + str(pdp.id))

        # Get a Personalized Data Policy (PDP)
        retrieved_pdp = datasets.get_pdp(dataset.id, pdp.id)
        self.logger.info("Retrieved a Personalized Data Policy (PDP): " + retrieved_pdp.name + ", id: " + str(retrieved_pdp.id))

        # List Personalized Data Policies (PDP)
        pdp_list = datasets.list_pdps(dataset.id)
        self.logger.info("Retrieved a list containing " + str(len(pdp_list)) + " PDP(s) for DataSet " + str(dataset.id))

        # Update a Personalized Data Policy (PDP)
        pdp_filter.NOT = True  # Negate the previous filter (logical NOT)
        pdp_request.name = 'Only show friends not attending the party'
        pdp_request.filters = [pdp_filter]  # A single PDP can contain multiple filters
        pdp = datasets.update_pdp(dataset.id, pdp.id, pdp_request)
        self.logger.info("Updated a Personalized Data Policy (PDP): " + pdp.name + ", id: " + str(pdp.id))

        # Delete a Personalized Data Policy (PDP)
        datasets.delete_pdp(dataset.id, pdp.id)
        self.logger.info("Deleted a Personalized Data Policy (PDP) " + pdp.name + ", id: " + str(pdp.id))

        # Delete a DataSet
        datasets.delete(dataset.id)
        self.logger.info("Deleted DataSet " + str(dataset.id))

    # Streams are useful for uploading massive data sources in chunks, in parallel
    # Streams are also useful with data sources that are constantly changing/growing
    def streams(self):
        # Streams Docs: https://developer.domo.com/docs/data-apis/data
        self.logger.info("\n**** Domo API - Stream Examples ****\n")
        streams = self.domo.streams

        # Define a DataSet Schema to populate the Stream Request
        dsr = DataSetRequest()
        dsr.name = 'Leonhard Euler Party'
        dsr.description = 'Mathematician Guest List'
        dsr.schema = Schema([Column(ColumnType.STRING, 'Friend'), Column(ColumnType.STRING, 'Attending')])

        # Build a Stream Request
        stream_request = CreateStreamRequest(dsr, UpdateMethod.APPEND)

        # Create a Stream w/DataSet
        stream = streams.create(stream_request)
        self.logger.info("Created Stream " + str(stream.id) + " containing the new DataSet " + stream.dataSet.id)

        # Get a Stream's metadata
        retrieved_stream = streams.get(stream.id)
        self.logger.info("Retrieved Stream " + str(retrieved_stream.id) + " containing DataSet " + retrieved_stream.dataSet.id)

        # List Streams
        limit = 1000
        offset = 0
        stream_list = streams.list(limit, offset)
        self.logger.info("Retrieved a list containing " + str(len(stream_list)) + " Stream(s)")

        # Update a Stream's metadata
        stream_update = CreateStreamRequest(dsr, UpdateMethod.REPLACE)
        updated_stream = streams.update(retrieved_stream.id, stream_update)
        self.logger.info("Updated Stream " + str(updated_stream.id) + " to update method: " + updated_stream.updateMethod)

        # Search for Streams
        stream_property = 'dataSource.name: ' + dsr.name
        searched_streams = streams.search(stream_property)
        self.logger.info("Stream search: there are " + str(len(searched_streams)) + " Stream(s) with the DataSet title: " + dsr.name)

        # Create an Execution (Begin an upload process)
        execution = streams.create_execution(stream.id)
        self.logger.info("Created Execution " + str(execution.id) + " for Stream " + str(stream.id))

        # Get an Execution
        retrieved_execution = streams.get_execution(stream.id, execution.id)
        self.logger.info("Retrieved Execution with id: " + str(retrieved_execution.id))

        # List Executions
        execution_list = streams.list_executions(stream.id, limit, offset)
        self.logger.info("Retrieved a list containing " + str(len(execution_list)) + " Execution(s)")

        # Upload Data: Multiple Parts can be uploaded in parallel
        part = 1
        csv = "\"Pythagoras\",\"FALSE\"\n\"Alan Turing\",\"TRUE\"\n\"George Boole\",\"TRUE\""
        execution = streams.upload_part(stream.id, execution.id, part, csv)

        # Commit the execution (End an upload process)(Executions/commits are NOT atomic)
        committed_execution = streams.commit_execution(stream.id, execution.id)
        self.logger.info("Committed Execution " + str(committed_execution.id) + " on Stream " + str(stream.id))

        # Abort a specific Execution
        execution = streams.create_execution(stream.id)
        aborted_execution = streams.abort_execution(stream.id, execution.id)
        self.logger.info("Aborted Execution " + str(aborted_execution.id) + " on Stream " + str(stream.id))

        # Abort any Execution on a given Stream
        streams.create_execution(stream.id)
        streams.abort_current_execution(stream.id)
        self.logger.info("Aborted Executions on Stream " + str(stream.id))

        # Delete a Stream
        streams.delete(stream.id)
        self.logger.info("Deleted Stream " + str(stream.id) + "; the associated DataSet must be deleted separately")

        # Delete the associated DataSet
        self.domo.datasets.delete(stream.dataSet.id)

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
        user_list = users.get(user.id)
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

    def groups(self):
        # Group Docs: https://developer.domo.com/docs/domo-apis/group-apis
        self.logger.info("\n**** Domo API - Group Examples ****\n")
        groups = self.domo.groups
    
        # Build a Group
        group_request = CreateGroupRequest()
        group_request.name = 'Groupy Group ' + str(randint(0, 10000))
        group_request.active = True
        group_request.default = False

        # Create a Group
        group = groups.create(group_request)
        self.logger.info("Created Group '" + group.name + "'")
    
        # Get a Group
        group = groups.get(group.id)
        self.logger.info("Retrieved Group '" + group.name + "'")

        # List Groups
        group_list = groups.get(group.id)
        self.logger.info("Retrieved a list containing " + str(len(group_list)) + " Group(s)")

        # Update a Group
        group_update = CreateGroupRequest()
        group_update.name = 'Groupy Group ' + str(randint(0, 10000))
        group_update.active = False
        group_update.default = False
        group = groups.update(group.id, group_update)
        self.logger.info("Updated Group '" + group.name + "'")

        # Add a User to a Group
        user_list = self.domo.users.list(10, 0)  # Retrieve the first listed user
        user = user_list[0]
        groups.add_user(group.id, user.id)
        self.logger.info("Added User " + str(user.id) + " to Group " + str(group.id))

        # List Users in a Group
        user_list = groups.list_users(group.id)
        self.logger.info("Retrieved a User list from a Group containing " + str(len(user_list)) + " User(s)")

        # Remove a User from a Group
        groups.remove_user(group.id, user.id)
        self.logger.info("Removed User " + str(user.id) + " from Group " + str(group.id))

        # Delete a Group
        groups.delete(group.id)
        self.logger.info("Deleted group '" + group.name + "'")


examples = DomoSDKExamples()
examples.datasets()
examples.streams()
examples.users()
examples.groups()
