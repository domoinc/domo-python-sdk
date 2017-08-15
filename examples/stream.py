from pydomo.datasets import DataSetRequest, Schema, Column, ColumnType
from pydomo.streams import UpdateMethod, CreateStreamRequest


def streams(domo):
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
