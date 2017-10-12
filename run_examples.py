'''

Domo Python SDK Usage

!!! NOTICE !!!: This SDK is written for Python3. Python2 is not compatible. Execute all scripts via 'python3 myFile.py'

- To run this example file:
-- Copy and paste the contents of this file
-- Plug in your CLIENT_ID and CLIENT_SECRET (https://developer.domo.com/manage-clients), and execute "python3 run_examples.py"

- These tests clean up after themselves; several objects are created and deleted on your Domo instance
- If you encounter a 'Not Allowed' error, this is a permissions issue. Please speak with your Domo Administrator.
- If you encounter a 'Forbidden' error, your OAuth client is likely missing the scope required for that endpoint

- Note that the Domo objects used in these examples are dictionaries that prevent you from accidentally setting the wrong fields.
- Standard dictionaries may be supplied instead of the defined objects (Schema, DataSetRequest, etc)
- All returned objects are dictionaries

'''

import logging
import random
from pydomo import Domo
from pydomo.datasets import DataSetRequest, Schema, Column, ColumnType, Policy
from pydomo.datasets import PolicyFilter, FilterOperator, PolicyType, Sorting
from pydomo.users import CreateUserRequest
from pydomo.datasets import DataSetRequest, Schema, Column, ColumnType
from pydomo.streams import UpdateMethod, CreateStreamRequest
from pydomo.groups import CreateGroupRequest


# My Domo Client ID and Secret (https://developer.domo.com/manage-clients)
CLIENT_ID = 'MY_CLIENT_ID'
CLIENT_SECRET = 'MY_CLIENT_SECRET'

# The Domo API host domain. This can be changed as needed - for use with a proxy or test environment
API_HOST = 'api.domo.com'


class DomoSDKExamples:
    def __init__(self):
        domo = self.init_domo_client(CLIENT_ID, CLIENT_SECRET)
        self.datasets(domo)
        self.streams(domo)
        self.users(domo)
        self.groups(domo)
        self.pages(domo)

    ############################
    # INIT SDK CLIENT
    ############################
    def init_domo_client(self, client_id, client_secret, **kwargs):
        '''

        - Create an API client on https://developer.domo.com
        - Initialize the Domo SDK with your API client id/secret
        - If you have multiple API clients you would like to use, simply initialize multiple Domo() instances
        - Docs: https://developer.domo.com/docs/domo-apis/getting-started

        '''
        handler = logging.StreamHandler()
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logging.getLogger().addHandler(handler)

        return Domo(client_id, client_secret, logger_name='foo', log_level=logging.INFO, api_host=API_HOST, **kwargs)


    ############################
    # DATASETS
    ############################
    def datasets(self, domo):
        '''

        DataSets are useful for data sources that only require occasional replacement. See the docs at
        https://developer.domo.com/docs/data-apis/data

        '''
        domo.logger.info("\n**** Domo API - DataSet Examples ****\n")
        datasets = domo.datasets

        # Define a DataSet Schema
        dsr = DataSetRequest()
        dsr.name = 'Leonhard Euler Party'
        dsr.description = 'Mathematician Guest List'
        dsr.schema = Schema([Column(ColumnType.STRING, 'Friend')])

        # Create a DataSet with the given Schema
        dataset = datasets.create(dsr)
        domo.logger.info("Created DataSet " + dataset['id'])

        # Get a DataSets's metadata
        retrieved_dataset = datasets.get(dataset['id'])
        domo.logger.info("Retrieved DataSet " + retrieved_dataset['id'])

        # List DataSets
        dataset_list = list(datasets.list(sort=Sorting.NAME, limit=10))
        domo.logger.info("Retrieved a list containing {} DataSet(s)".format(
            len(dataset_list)))

        # Update a DataSets's metadata
        update = DataSetRequest()
        update.name = 'Leonhard Euler Party - Update'
        update.description = 'Mathematician Guest List - Update'
        update.schema = Schema([Column(ColumnType.STRING, 'Friend'),
                                Column(ColumnType.STRING, 'Attending')])
        updated_dataset = datasets.update(dataset['id'], update)
        domo.logger.info("Updated DataSet {}: {}".format(updated_dataset['id'],
                                                         updated_dataset['name']))

        # Import Data from a string
        csv_upload = '"Pythagoras","FALSE"\n"Alan Turing","TRUE"\n' \
                     '"George Boole","TRUE"'
        datasets.data_import(dataset['id'], csv_upload)
        domo.logger.info("Uploaded data to DataSet " + dataset['id'])

        # Export Data to a string
        include_csv_header = True
        csv_download = datasets.data_export(dataset['id'], include_csv_header)
        domo.logger.info("Downloaded data from DataSet {}:\n{}".format(
            dataset['id'], csv_download))

        # Export Data to a file (also returns a readable/writable file object)
        csv_file_path = './math.csv'
        include_csv_header = True
        csv_file = datasets.data_export_to_file(dataset['id'], csv_file_path,
                                                include_csv_header)
        csv_file.close()
        domo.logger.info("Downloaded data as a file from DataSet {}".format(
            dataset['id']))

        # Import Data from a file
        csv_file_path = './math.csv'
        datasets.data_import_from_file(dataset['id'], csv_file_path)
        domo.logger.info("Uploaded data from a file to DataSet {}".format(
            dataset['id']))

        #########################################
        # Personalized Data Policies (PDPs)
        #########################################

        # Build a Policy Filter (hide sensitive columns/values from users)
        pdp_filter = PolicyFilter()
        pdp_filter.column = 'Attending'  # The DataSet column to filter on
        pdp_filter.operator = FilterOperator.EQUALS
        pdp_filter.values = ['TRUE']  # The DataSet row value to filter on

        # Build the Personalized Data Policy (PDP)
        pdp_request = Policy()
        pdp_request.name = 'Only show friends attending the party'
        # A single PDP can contain multiple filters
        pdp_request.filters = [pdp_filter]
        pdp_request.type = PolicyType.USER
        # The affected user ids (restricted access by filter)
        pdp_request.users = [998, 999]
        # The affected group ids (restricted access by filter)
        pdp_request.groups = [99, 100]

        # Create the PDP
        pdp = datasets.create_pdp(dataset['id'], pdp_request)
        domo.logger.info("Created a Personalized Data Policy (PDP): "
                         "{}, id: {}".format(pdp['name'], pdp['id']))

        # Get a Personalized Data Policy (PDP)
        pdp = datasets.get_pdp(dataset['id'], pdp['id'])
        domo.logger.info("Retrieved a Personalized Data Policy (PDP):"
                         " {}, id: {}".format(pdp['name'], pdp['id']))

        # List Personalized Data Policies (PDP)
        pdp_list = datasets.list_pdps(dataset['id'])
        domo.logger.info("Retrieved a list containing {} PDP(s) for DataSet {}"
                         .format(len(pdp_list), dataset['id']))

        # Update a Personalized Data Policy (PDP)
        # Negate the previous filter (logical NOT). Note that in this case you
        # must treat the object as a dictionary - `pdp_filter.not` is invalid
        # syntax.
        pdp_filter['not'] = True
        pdp_request.name = 'Only show friends not attending the party'
        # A single PDP can contain multiple filters
        pdp_request.filters = [pdp_filter]
        pdp = datasets.update_pdp(dataset['id'], pdp['id'], pdp_request)
        domo.logger.info("Updated a Personalized Data Policy (PDP): {}, id: {}"
                         .format(pdp['name'], pdp['id']))

        # Delete a Personalized Data Policy (PDP)
        datasets.delete_pdp(dataset['id'], pdp['id'])
        domo.logger.info("Deleted a Personalized Data Policy (PDP): {}, id: {}"
                         .format(pdp['name'], pdp['id']))

        # Delete a DataSet
        datasets.delete(dataset['id'])
        domo.logger.info("Deleted DataSet {}".format(dataset['id']))


    ############################
    # STREAMS
    ############################
    def streams(self, domo):
        '''Streams are useful for uploading massive data sources in
        chunks, in parallel. They are also useful with data sources that
        are constantly changing/growing.
        Streams Docs: https://developer.domo.com/docs/data-apis/data
        '''
        domo.logger.info("\n**** Domo API - Stream Examples ****\n")
        streams = domo.streams

        # Define a DataSet Schema to populate the Stream Request
        dsr = DataSetRequest()
        dsr.name = 'Leonhard Euler Party'
        dsr.description = 'Mathematician Guest List'
        dsr.schema = Schema([Column(ColumnType.STRING, 'Friend'),
                             Column(ColumnType.STRING, 'Attending')])

        # Build a Stream Request
        stream_request = CreateStreamRequest(dsr, UpdateMethod.APPEND)

        # Create a Stream w/DataSet
        stream = streams.create(stream_request)
        domo.logger.info("Created Stream {} containing the new DataSet {}"
                         .format(stream['id'], stream['dataSet']['id']))

        # Get a Stream's metadata
        retrieved_stream = streams.get(stream['id'])
        domo.logger.info("Retrieved Stream {} containing DataSet {}".format(
            retrieved_stream['id'], retrieved_stream['dataSet']['id']))

        # List Streams
        limit = 1000
        offset = 0
        stream_list = streams.list(limit, offset)
        domo.logger.info("Retrieved a list containing {} Stream(s)".format(
            len(stream_list)))

        # Update a Stream's metadata
        stream_update = CreateStreamRequest(dsr, UpdateMethod.REPLACE)
        updated_stream = streams.update(retrieved_stream['id'], stream_update)
        domo.logger.info("Updated Stream {} to update method: {}".format(
            updated_stream['id'], updated_stream['updateMethod']))

        # Search for Streams
        stream_property = 'dataSource.name:' + dsr.name
        searched_streams = streams.search(stream_property)
        domo.logger.info("Stream search: there are {} Stream(s) with the DataSet "
                         "title: {}".format(len(searched_streams), dsr.name))

        # Create an Execution (Begin an upload process)
        execution = streams.create_execution(stream['id'])
        domo.logger.info("Created Execution {} for Stream {}".format(
            execution['id'], stream['id']))

        # Get an Execution
        retrieved_execution = streams.get_execution(stream['id'],
                                                    execution['id'])
        domo.logger.info("Retrieved Execution with id: {}".format(
            retrieved_execution['id']))

        # List Executions
        execution_list = streams.list_executions(stream['id'], limit, offset)
        domo.logger.info("Retrieved a list containing {} Execution(s)".format(
            len(execution_list)))

        # Upload Data: Multiple Parts can be uploaded in parallel
        part = 1
        csv = '"Pythagoras","FALSE"\n"Alan Turing","TRUE"'
        execution = streams.upload_part(stream['id'], execution['id'],
                                        part, csv)

        part = 2
        csv = '"George Boole","TRUE"'
        execution = streams.upload_part(stream['id'], execution['id'],
                                        part, csv)

        # Commit the execution (End an upload process)
        # Executions/commits are NOT atomic
        committed_execution = streams.commit_execution(stream['id'],
                                                       execution['id'])
        domo.logger.info("Committed Execution {} on Stream {}".format(
            committed_execution['id'], stream['id']))

        # Abort a specific Execution
        execution = streams.create_execution(stream['id'])
        aborted_execution = streams.abort_execution(stream['id'],
                                                    execution['id'])
        domo.logger.info("Aborted Execution {} on Stream {}".format(
            aborted_execution['id'], stream['id']))

        # Abort any Execution on a given Stream
        streams.create_execution(stream['id'])
        streams.abort_current_execution(stream['id'])
        domo.logger.info("Aborted Executions on Stream {}".format(
            stream['id']))

        # Delete a Stream
        streams.delete(stream['id'])
        domo.logger.info("Deleted Stream {}; the associated DataSet must be "
                         "deleted separately".format(stream['id']))

        # Delete the associated DataSet
        domo.datasets.delete(stream['dataSet']['id'])


    ############################
    # USERS
    ############################
    def users(self, domo):
        '''User Docs: https://developer.domo.com/docs/domo-apis/users
        '''
        domo.logger.info("\n**** Domo API - User Examples ****\n")

        # Build a User
        user_request = CreateUserRequest()
        user_request.name = 'Leonhard Euler'
        user_request.email = 'leonhard.euler{}@domo.com'.format(random.randint(0, 10000))
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
        user_update.email = 'leo.euler{}@domo.com'.format(random.randint(0, 10000))
        user_update.role = 'Privileged'
        user = domo.users.update(user['id'], user_update)
        domo.logger.info("Updated User '{}': {}".format(user['name'],
                                                        user['email']))

        # Delete a User
        domo.users.delete(user['id'])
        domo.logger.info("Deleted User '{}'".format(user['name']))


    ############################
    # GROUPS
    ############################
    def groups(self, domo):
        '''Group Docs:
        https://developer.domo.com/docs/domo-apis/group-apis
        '''
        domo.logger.info("\n**** Domo API - Group Examples ****\n")
        groups = domo.groups

        # Build a Group
        group_request = CreateGroupRequest()
        group_request.name = 'Groupy Group {}'.format(random.randint(0, 10000))
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
        group_update.name = 'Groupy Group {}'.format(random.randint(0, 10000))
        group_update.active = False
        group_update.default = False
        group = groups.update(group['id'], group_update)
        domo.logger.info("Updated Group '{}'".format(group['name']))

        # Add a User to a Group
        user_list = domo.users.list(10, 0)
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


    ############################
    # PAGES
    ############################
    def pages(self, domo):
        '''Page Docs: https://developer.domo.com/docs/domo-apis/pages
        '''
        domo.logger.info("\n**** Domo API - Page Examples ****\n")

        # Create a page
        page = domo.pages.create('New Page')
        domo.logger.info("Created Page {}".format(page['id']))

        # Create a subpage
        subpage = domo.pages.create('Sub Page', parentId=page['id'])
        domo.logger.info("Created Subpage {}".format(subpage['id']))

        # Update the page using returned page
        page['name'] = 'Updated Page'
        domo.pages.update(**page)
        domo.logger.info("Renamed Page {}".format(page['id']))

        # Turn subpage into to top-level page using keyword argument
        domo.pages.update(subpage['id'], parentId=None)
        domo.logger.info("Moved Page to top level {}".format(subpage['id']))

        # Get the page
        page = domo.pages.get(page['id'])

        # List pages
        page_list = list(domo.pages.list())
        domo.logger.info("Retrieved a list of {} top-level page(s)".format(
            len(page_list)))

        # Create a few collections
        collections = [
            domo.pages.create_collection(page['id'], 'First Collection'),
            domo.pages.create_collection(page['id'], 'Second Collection'),
        ]
        domo.logger.info("Created two collections on page {}".format(page['id']))

        # Get collections
        collection_list = domo.pages.get_collections(page['id'])
        domo.logger.info("Retrieved a list of {} collections".format(
            len(collection_list)))

        # Update collection
        collections[1]['title'] = 'Last Collection'
        domo.pages.update_collection(page['id'], **collections[1])
        domo.logger.info("Updated collection {}: {}".format(collections[1]['id'],
                                                            collections[1]['title']))

        # Clean up
        for collection in collections:
            domo.pages.delete_collection(page['id'], collection['id'])
        domo.pages.delete(page['id'])
        domo.pages.delete(subpage['id'])
        domo.logger.info("Deleted collections and pages")

DomoSDKExamples()  # Execute the script
