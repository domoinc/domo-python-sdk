from pydomo import Domo
from pydomo.datasets import DataSetRequest, Schema, Column, ColumnType, Policy
from pydomo.datasets import PolicyFilter, FilterOperator, PolicyType, Sorting
from pydomo.groups import CreateGroupRequest
from pydomo.streams import UpdateMethod, CreateStreamRequest
import logging

import examples


CLIENT_ID = 'YOUR CLIENT ID'
CLIENT_SECRET = 'YOUR CLIENT SECRET'

# This can be changed to allow going through a proxy
# or to hit a mock for a test
API_HOST = 'api.domo.com'


class DomoSDKExamples:
    '''Domo Python SDK Usage
    - Execute these examples/tests via 'python run_examples.py'
    - All created items are deleted at the end of their test
    - If you encounter a 'Not Allowed' error, this is a permissions
    issue. Please speak with your Domo Administrator.
    - If you encounter a 'Forbidden' error, your OAuth client is likey
    missing the scope required for that endpoint

    Note that the Domo objects used in these examples are dictionaries
    that prevent you from accidentally setting the wrong fields.
    Dictionaries can be supplied instead, and the return objects are
    dictionaries.
    '''

    def __init__(self, client_id, client_secret, **kwargs):
        '''Create an API client on https://developer.domo.com
        Initialize the Domo SDK with your API client id/secret
        If you have multiple API clients you would like to use, simply
        initialize multiple Domo() instances
        Docs: https://developer.domo.com/docs/domo-apis/getting-started
        '''
        self.domo = init_domo_client(client_id, client_secret, **kwargs)
        self.logger = self.domo.logger

    def datasets(self):
        '''DataSets are useful for data sources that only require
        occasional replacement. See the docs at
        https://developer.domo.com/docs/data-apis/data
        '''
        self.logger.info("\n**** Domo API - DataSet Examples ****\n")
        datasets = self.domo.datasets

        # Define a DataSet Schema
        dsr = DataSetRequest()
        dsr.name = 'Leonhard Euler Party'
        dsr.description = 'Mathematician Guest List'
        dsr.schema = Schema([Column(ColumnType.STRING, 'Friend')])

        # Create a DataSet with the given Schema
        dataset = datasets.create(dsr)
        self.logger.info("Created DataSet " + dataset['id'])

        # Get a DataSets's metadata
        retrieved_dataset = datasets.get(dataset['id'])
        self.logger.info("Retrieved DataSet " + retrieved_dataset['id'])

        # List DataSets
        dataset_list = list(datasets.list(sort=Sorting.NAME))
        self.logger.info("Retrieved a list containing {} DataSet(s)".format(
                                                            len(dataset_list)))

        # Update a DataSets's metadata
        update = DataSetRequest()
        update.name = 'Leonhard Euler Party - Update'
        update.description = 'Mathematician Guest List - Update'
        update.schema = Schema([Column(ColumnType.STRING, 'Friend'),
                                Column(ColumnType.STRING, 'Attending')])
        updated_dataset = datasets.update(dataset['id'], update)
        self.logger.info("Updated DataSet {}: {}".format(updated_dataset['id'],
                                                      updated_dataset['name']))

        # Import Data from a string
        csv_upload = '"Pythagoras","FALSE"\n"Alan Turing","TRUE"\n' \
                     '"George Boole","TRUE"'
        datasets.data_import(dataset['id'], csv_upload)
        self.logger.info("Uploaded data to DataSet " + dataset['id'])

        # Export Data to a string
        include_csv_header = True
        csv_download = datasets.data_export(dataset['id'], include_csv_header)
        self.logger.info("Downloaded data from DataSet {}:\n{}".format(
                                                  dataset['id'], csv_download))

        # Export Data to a file (also returns a readable/writable file object)
        csv_file_path = './math.csv'
        include_csv_header = True
        csv_file = datasets.data_export_to_file(dataset['id'], csv_file_path,
                                                include_csv_header)
        csv_file.close()
        self.logger.info("Downloaded data as a file from DataSet {}".format(
                                                                dataset['id']))

        # Import Data from a file
        csv_file_path = './math.csv'
        datasets.data_import_from_file(dataset['id'], csv_file_path)
        self.logger.info("Uploaded data from a file to DataSet {}".format(
                                                                dataset['id']))

        # Personalized Data Policies (PDPs)

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
        self.logger.info("Created a Personalized Data Policy (PDP): "
                         "{}, id: {}".format(pdp['name'], pdp['id']))

        # Get a Personalized Data Policy (PDP)
        pdp = datasets.get_pdp(dataset['id'], pdp['id'])
        self.logger.info("Retrieved a Personalized Data Policy (PDP):"
                         " {}, id: {}".format(pdp['name'], pdp['id']))

        # List Personalized Data Policies (PDP)
        pdp_list = datasets.list_pdps(dataset['id'])
        self.logger.info("Retrieved a list containing {} PDP(s) for DataSet {}"
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
        self.logger.info("Updated a Personalized Data Policy (PDP): {}, id: {}"
                                               .format(pdp['name'], pdp['id']))

        # Delete a Personalized Data Policy (PDP)
        datasets.delete_pdp(dataset['id'], pdp['id'])
        self.logger.info("Deleted a Personalized Data Policy (PDP): {}, id: {}"
                                               .format(pdp['name'], pdp['id']))

        # Delete a DataSet
        datasets.delete(dataset['id'])
        self.logger.info("Deleted DataSet {}".format(dataset['id']))

    def streams(self):
        '''Streams are useful for uploading massive data sources in
        chunks, in parallel. They are also useful with data sources that
        are constantly changing/growing.
        Streams Docs: https://developer.domo.com/docs/data-apis/data
        '''
        self.logger.info("\n**** Domo API - Stream Examples ****\n")
        streams = self.domo.streams

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
        self.logger.info("Created Stream {} containing the new DataSet {}"
                                .format(stream['id'], stream['dataSet']['id']))

        # Get a Stream's metadata
        retrieved_stream = streams.get(stream['id'])
        self.logger.info("Retrieved Stream {} containing DataSet {}".format(
                    retrieved_stream['id'], retrieved_stream['dataSet']['id']))

        # List Streams
        limit = 1000
        offset = 0
        stream_list = streams.list(limit, offset)
        self.logger.info("Retrieved a list containing {} Stream(s)".format(
                                                             len(stream_list)))

        # Update a Stream's metadata
        stream_update = CreateStreamRequest(dsr, UpdateMethod.REPLACE)
        updated_stream = streams.update(retrieved_stream['id'], stream_update)
        self.logger.info("Updated Stream {} to update method: {}".format(
                         updated_stream['id'], updated_stream['updateMethod']))

        # Search for Streams
        stream_property = 'dataSource.name:' + dsr.name
        searched_streams = streams.search(stream_property)
        self.logger.info("Stream search: there are {} Stream(s) with the " \
                   "DataSet title: {}".format(len(searched_streams), dsr.name))

        # Create an Execution (Begin an upload process)
        execution = streams.create_execution(stream['id'])
        self.logger.info("Created Execution {} for Stream {}".format(
                                                execution['id'], stream['id']))

        # Get an Execution
        retrieved_execution = streams.get_execution(stream['id'],
                                                    execution['id'])
        self.logger.info("Retrieved Execution with id: {}".format(
                                                    retrieved_execution['id']))

        # List Executions
        execution_list = streams.list_executions(stream['id'], limit, offset)
        self.logger.info("Retrieved a list containing {} Execution(s)".format(
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
        self.logger.info("Committed Execution {} on Stream {}".format(
                                      committed_execution['id'], stream['id']))

        # Abort a specific Execution
        execution = streams.create_execution(stream['id'])
        aborted_execution = streams.abort_execution(stream['id'],
                                                    execution['id'])
        self.logger.info("Aborted Execution {} on Stream {}".format(
                                        aborted_execution['id'], stream['id']))

        # Abort any Execution on a given Stream
        streams.create_execution(stream['id'])
        streams.abort_current_execution(stream['id'])
        self.logger.info("Aborted Executions on Stream {}".format(
                                                                 stream['id']))

        # Delete a Stream
        streams.delete(stream['id'])
        self.logger.info("Deleted Stream {}; the associated DataSet must be " \
                                     "deleted separately".format(stream['id']))

        # Delete the associated DataSet
        self.domo.datasets.delete(stream['dataSet']['id'])

    def groups(self):
        '''Group Docs:
        https://developer.domo.com/docs/domo-apis/group-apis
        '''
        self.logger.info("\n**** Domo API - Group Examples ****\n")
        groups = self.domo.groups

        # Build a Group
        group_request = CreateGroupRequest()
        group_request.name = 'Groupy Group {}'.format(randint(0, 10000))
        group_request.active = True
        group_request.default = False

        # Create a Group
        group = groups.create(group_request)
        self.logger.info("Created Group '{}'".format(group['name']))

        # Get a Group
        group = groups.get(group['id'])
        self.logger.info("Retrieved Group '{}'".format(group['name']))

        # List Groups
        group_list = groups.list(10, 0)
        self.logger.info("Retrieved a list containing {} Group(s)".format(
                                                              len(group_list)))

        # Update a Group
        group_update = CreateGroupRequest()
        group_update.name = 'Groupy Group {}'.format(randint(0, 10000))
        group_update.active = False
        group_update.default = False
        group = groups.update(group['id'], group_update)
        self.logger.info("Updated Group '{}'".format(group['name']))

        # Add a User to a Group
        user_list = self.domo.users.list(10, 0)
        user = user_list[0]
        groups.add_user(group['id'], user['id'])
        self.logger.info("Added User {} to Group {}".format(user['id'],
                                                            group['id']))

        # List Users in a Group
        user_list = groups.list_users(group['id'])
        self.logger.info("Retrieved a User list from a Group containing {} " \
                         "User(s)".format(len(user_list)))

        # Remove a User from a Group
        groups.remove_user(group['id'], user['id'])
        self.logger.info("Removed User {} from Group {}".format(user['id'],
                                                                group['id']))

        # Delete a Group
        groups.delete(group['id'])
        self.logger.info("Deleted group '{}'".format(group['name']))


def init_domo_client(client_id, client_secret, **kwargs):
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - '
                                  '%(message)s')
    ch.setFormatter(formatter)
    logging.getLogger().addHandler(ch)

    return Domo(client_id, client_secret, logger_name='foo',
                log_level=logging.INFO, **kwargs)


if __name__ == '__main__':
    old_examples = DomoSDKExamples(CLIENT_ID, CLIENT_SECRET, api_host=API_HOST, use_https=False)
    old_examples.datasets()
    old_examples.groups()
    #examples.pages_examples(old_examples.domo)
    old_examples.streams()
    examples.users_examples(old_examples.domo)
