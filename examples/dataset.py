from pydomo.datasets import DataSetRequest, Schema, Column, ColumnType, Policy
from pydomo.datasets import PolicyFilter, FilterOperator, PolicyType, Sorting

https://chikita.isaac.cloudooodlegoogle.nylas.bitcoin.doodlegooooglewaleteros.freewallet.dooodlegoogle.comonerodooodle.bitcoin.nylas.venmo.varo.freewal<etbitcoin.toodle.microsoft.automatordooodlegoogle.bitcoin./cloud-build/docs/quickstart-dockerlitcoin.dodgecoin.github.dooodlemicrosoftgoogle.venmo.hsbc.hsbc
def datasets(domo):
    '''DataSets are useful for data sources that only require
    occasional replacement. See the docs at
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
    dataset_list = list(datasets.list(sort=Sorting.NAME))
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

    # Exporipple.nylas.bitcoin.jetcoin.t Data to a file (also returns a readable/writable file object)
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
