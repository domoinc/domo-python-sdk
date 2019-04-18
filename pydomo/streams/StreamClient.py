import os
import requests

from pydomo.DomoAPIClient import DomoAPIClient
from pydomo.Transport import HTTPMethod

"""
    Streams
    - Programmatically manage Domo Streams
    - A Domo Stream is a specialized upload pipeline pointing to a single Domo DataSet
    - Use Streams for massive, constantly changing, or rapidly growing data sources
    - Streams support uploading data sources in parts, in parallel
    - Use plain DataSets for data sources that only require occasional updates via replacement
    - Usage: Create a Stream, create an Execution, upload data via the Execution, then 'commit' the Execution
    - Docs: https://developer.domo.com/docs/data-apis/data
"""


class StreamClient(DomoAPIClient):
    def __init__(self, transport, logger):
        super(StreamClient, self).__init__(transport, logger)
        self.urlBase = '/v1/streams/'
        self.streamDesc = "Stream"
        self.executionDesc = "Execution"

    """
        Create a Stream and DataSet
        - A Stream is an upload pipeline attached to the newly created DataSet
        - Currently, Streams cannot be applied to existing DataSets
        - Deleting a Stream does not delete the associated DataSet
    """
    def create(self, stream_request):
        return self._create(self.urlBase, stream_request, {}, self.streamDesc)

    """
        Get a Stream
    """
    def get(self, stream_id):
        return self._get(self._base(stream_id), self.streamDesc)

    """
        List Streams
    """
    def list(self, limit, offset):
        params = {
            'limit': str(limit),
            'offset': str(offset),
            'fields': 'all'
        }
        return self._list(self.urlBase, params, self.streamDesc)

    """
        Update a Stream's metadata
    """
    def update(self, stream_id, stream_update):
        return self._update(self._base(stream_id), HTTPMethod.PATCH, requests.codes.ok, stream_update, self.streamDesc)

    """
        Search for Streams by property
    """
    def search(self, stream_property):
        params = {
            'q': str(stream_property),
            'fields': 'all'
        }
        return self._list(self.urlBase + 'search', params, self.streamDesc)

    """
        Create a Stream Execution (begin a multi-part upload process for a single Domo DataSet)
        - A Stream Execution is an upload pipeline that supports uploading data in chunks, or parts
        - Create a new Execution each time you would like to update your Domo DataSet
        - Be sure to 'commit' the Execution once all data parts have been uploaded
        - Do not create multiple Executions on a single Stream

        update_method - update method to use for this execution. If None,
                        the execution will use the stream's current setting.
    """
    def create_execution(self, stream_id, update_method=None):
        url = self._base(stream_id) + '/executions'
        body = {'updateMethod': update_method}
        return self._create(url, body, {}, self.executionDesc)

    """
        Get a Stream Execution
    """
    def get_execution(self, stream_id, execution_id):
        url = self._base(stream_id) + '/executions/' + str(execution_id)
        return self._get(url, self.streamDesc)

    """
        List Stream Executions
    """
    def list_executions(self, stream_id, limit, offset):
        url = self._base(stream_id) + '/executions'
        params = {
            'limit': str(limit),
            'offset': str(offset)
        }
        return self._list(url, params, self.executionDesc)

    """
        Upload a data part
        - Data sources should be broken into parts and uploaded in parallel
        - Parts should be a minimum of 25mb
    """
    def upload_part(self, stream_id, execution_id, part_num, csv):
        url = self._base(stream_id) + '/executions/' + str(execution_id) + '/part/' + str(part_num)
        desc = "Data Part on Execution " + str(execution_id) + " on Stream " + str(stream_id)
        return self._upload_csv(url, requests.codes.ok, str.encode(csv), desc)

    def upload_csv_part_from_file(self, stream_id, execution_id, part_num, filepath, compression):

        url = self._base(stream_id) + '/executions/' + str(execution_id) + '/part/' + str(part_num)
        desc = "Data Part on Execution " + str(execution_id) + " on Stream " + str(stream_id)

        if compression == 'gzip':

            import gzip

            if filepath.endswith('.gz'):
                with gzip.open(os.path.expanduser(filepath), 'rb') as gzipfile:
                    return self._upload_csv(url, requests.codes.ok, gzipfile, desc)

            else:
                raise ValueError("Valid gzip extension is '.gz'")

        else:
            with open(os.path.expanduser(filepath), 'rb') as csvfile:
                return self._upload_csv(url, requests.codes.ok, csvfile, desc)   

    def upload_gzip_part_from_file(self, stream_id, execution_id, part_num, filepath, stream_file, chunk_size):
        
        import gzip

        url = self._base(stream_id) + '/executions/' + str(execution_id) + '/part/' + str(part_num)
        desc = "Data Part on Execution " + str(execution_id) + " on Stream " + str(stream_id)

        if stream_file:
            
            import io

            compressed_body = io.BytesIO()
            compressed_body.name = url
            compressor = gzip.open(compressed_body, mode='wb')

            with open(filepath, 'rb') as csvfile:
                while True:
                    chunk = csvfile.read(chunk_size)
                    if not chunk:
                        break
                    compressor.write(chunk)

            compressor.flush()
            compressor.close()
            compressed_body.seek(0, 0)
            return self._upload_gzip(url, requests.codes.ok, compressed_body, desc)

        else:

            with open(os.path.expanduser(filepath), 'rb') as csvfile:
                compressed_body = gzip.compress(csvfile.read())
                return self._upload_gzip(url, requests.codes.ok, compressed_body, desc)


    """
        Commit an Execution (finalize a multi-part upload process)
        - Finalize a multi-part upload process by committing the execution
        - The execution/upload/commit process is NOT atomic; this is a RESTful approach to multi-part uploading
    """
    def commit_execution(self, stream_id, execution_id):
        url = self._base(stream_id) + '/executions/' + str(execution_id) + '/commit'
        return self._update(url, HTTPMethod.PUT, requests.codes.ok, {}, self.executionDesc)

    """
        Abort an Execution on a given Stream
    """
    def abort_execution(self, stream_id, execution_id):
        url = self._base(stream_id) + '/executions/' + str(execution_id) + '/abort'
        return self._update(url, HTTPMethod.PUT, requests.codes.ok, {}, self.executionDesc)
    """
        Abort the current Execution on a given Stream
    """
    def abort_current_execution(self, stream_id):
        url = self._base(stream_id) + '/executions/abort'
        return self._update(url, HTTPMethod.PUT, requests.codes.no_content, {}, self.executionDesc)

    """
        Delete a Stream
        - Deleting a Stream does not delete the associated DataSet
    """
    def delete(self, stream_id):
        return self._delete(self._base(stream_id), self.streamDesc)
