from pydomo.datasets import Sorting
from pydomo.DomoAPIClient import DomoAPIClient
from pydomo.Transport import HTTPMethod
import requests

"""
    DataSets
    - Programmatically manage Domo DataSets
    - Use DataSets for fairly static data sources that only require occasional updates via data replacement
    - Use Streams if your data source is massive, constantly changing, or rapidly growing
    - Docs: https://developer.domo.com/docs/data-apis/data
"""


class DataSetClient(DomoAPIClient):
    def __init__(self, transport, logger):
        super(DataSetClient, self).__init__(transport, logger)
        self.urlBase = '/v1/datasets/'
        self.dataSetDesc = "DataSet"
        self.PDPDesc = "Personalized Data Policy (PDP)"

    """
        Create a DataSet
    """
    def create(self, dataset_request):
        return self._create(self.urlBase, dataset_request, {}, self.dataSetDesc)

    """
        Get a DataSet
    """
    def get(self, dataset_id):
        return self._get(self._base(dataset_id), self.dataSetDesc)

    """
        List DataSets
        Returns a generator that will call the API multiple times
        If limit is supplied and non-zero, returns up to limit datasets
    """
    def list(self, sort=Sorting.DEFAULT, per_page=50, offset=0, limit=0):
        # API uses pagination with a max of 50 per page
        if per_page not in range(1, 51):
            raise ValueError('per_page must be between 1 and 50 (inclusive)')

        # Don't pull 50 values if user requests 10
        if limit:
            per_page = min(per_page, limit)

        params = {
            'sort': sort,
            'limit': per_page,
            'offset': offset,
        }
        dataset_count = 0

        datasets = self._list(self.urlBase, params, self.dataSetDesc)
        while datasets:
            for dataset in datasets:
                yield dataset
                dataset_count += 1
                if limit and dataset_count >= limit:
                    return

            params['offset'] += per_page
            if limit and params['offset'] + per_page > limit:
                # Don't need to pull more than the limit
                params['limit'] = limit - params['offset']
            datasets = self._list(self.urlBase, params, self.dataSetDesc)

    """
        Update a DataSet
    """
    def update(self, dataset_id, dataset_update):
        return self._update(self._base(dataset_id), HTTPMethod.PUT, requests.codes.ok, dataset_update, self.dataSetDesc)

    """
        Import data from a CSV string
    """
    def data_import(self, dataset_id, csv):
        url = self._base(dataset_id) + '/data'
        return self._upload_csv(url, requests.codes.no_content, csv, self.dataSetDesc)

    """
        Import data from a CSV file
    """
    def data_import_from_file(self, dataset_id, filepath):
        with open(filepath, 'rb') as csvfile:
            # passing an open file to the requests library invokes http streaming (uses minimal system memory)
            self.data_import(dataset_id, csvfile)

    """
        Export data to a CSV string
    """
    def data_export(self, dataset_id, include_csv_header):
        url = self._base(dataset_id) + '/data'
        params = {
            'includeHeader': str(include_csv_header),
            'fileName': 'foo.csv'
        }
        response = self.transport.get_csv(url=url, params=params)
        if response.status_code == requests.codes.ok:
            return response.text
        else:
            raise Exception("Error downloading data from DataSet: " + str(response.json()))

    """
        Export data to a CSV file, and return the readable/writable object file
    """
    def data_export_to_file(self, dataset_id, file_path, include_csv_header):
        file_path = str(file_path)
        if '.csv' not in file_path:
            file_path += '.csv'
        csv_str = self.data_export(dataset_id, include_csv_header)
        with open(file_path, "w") as csv_file:
            csv_file.write(csv_str)
        return open(file_path, "r+")  # return the file object as readable and writable

    """
        Delete a DataSet
    """
    def delete(self, dataset_id):
        return self._delete(self._base(dataset_id), self.dataSetDesc)

    """
        Create a Personalized Data Policy (PDP)
    """
    def create_pdp(self, dataset_id, pdp_request):
        url = self._base(dataset_id) + '/policies'
        return self._create(url, pdp_request, {}, self.PDPDesc)

    """
        Get a specific Personalized Data Policy (PDP) for a given DataSet
    """
    def get_pdp(self, dataset_id, policy_id):
        return self._get(self._base(dataset_id), self.PDPDesc)

    """
        List all Personalized Data Policies (PDPs) for a given DataSet
    """
    def list_pdps(self, dataset_id):
        url = self._base(dataset_id) + '/policies'
        return self._list(url, {}, self.dataSetDesc)

    """
        Update a specific Personalized Data Policy (PDP) for a given DataSet
    """
    def update_pdp(self, dataset_id, policy_id, policy_update):
        url = self._base(dataset_id) + '/policies/' + str(policy_id)
        return self._update(url, HTTPMethod.PUT, requests.codes.ok, policy_update, self.PDPDesc)

    """
        Delete a specific Personalized Data Policy (PDPs) for a given DataSet
    """
    def delete_pdp(self, dataset_id, policy_id):
        url = self._base(dataset_id) + '/policies/' + str(policy_id)
        return self._delete(url, self.PDPDesc)
