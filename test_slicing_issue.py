"""
This script tests the PyDomo SDK's data upload functionality using two different methods of slicing pandas DataFrames before uploading them as CSVs. 

The first method, `test_slicing_issue_old_method`, uses the current implementation of thee `stream_upload` method.

The second method, `test_slicing_issue_new_method`, uses a new `stream_upload` method where the slicing issue has been fixed.

Each method tries to create and update a Domo dataset using a test DataFrame. If dataset creation or update fails, the test will fail. The output of the script will indicate whether each method succeeded or failed, and any errors encountered will be printed to the console.
"""

import os
import unittest
import pandas as pd
import math
from pydomo import Domo
from pydomo.utilities import UtilitiesClient

DOMO_CLIENT_ID = os.getenv('DOMO_CLIENT_ID')
DOMO_CLIENT_SECRET = os.getenv('DOMO_CLIENT_SECRET')
DOMO_API_HOST = 'api.domo.com'

def stream_upload_new(self, ds_id, df_up, warn_schema_change=True):
    domoSchema = self.domo_schema(ds_id)
    dataSchema = self.data_schema(df_up)

    stream_id = self.get_stream_id(ds_id)

    if self.identical(domoSchema, dataSchema) == False:
        new_schema = {'schema': {'columns': dataSchema}}
        url = '/v1/datasets/{ds}'.format(ds=ds_id)
        change_result = self.transport.put(url, new_schema)
        if warn_schema_change:
            print('Schema Updated')

    exec_info = self.stream.create_execution(stream_id)
    exec_id = exec_info['id']

    chunksz = self.estimate_chunk_rows(df_up)
    start = 0
    df_rows = len(df_up.index)
    end = df_rows
    if df_rows > chunksz:
        end = chunksz

    for i in range(math.ceil(df_rows / chunksz)):
        df_sub = df_up.iloc[start:end]  # Removed the comma here
        csv = df_sub.to_csv(header=False, index=False)
        self.stream.upload_part(stream_id, exec_id, start, csv)
        start = end
        end = end + chunksz
        if end > df_rows:
            end = df_rows

    result = self.stream.commit_execution(stream_id, exec_id)
    return result

# Patch the UtilitiesClient class stream_upload method
UtilitiesClient.stream_upload_new = stream_upload_new

class TestSlicingIssue(unittest.TestCase):
    
    def setUp(self):
        self.domo = Domo(client_id=DOMO_CLIENT_ID, client_secret=DOMO_CLIENT_SECRET, api_host=DOMO_API_HOST)
        data = {
        'col1': [1, 2, 3, None],
        'col2': ['a', 'b', '', None],
        'col3': [1.1, 2.2, 3.3, None],
        'col4': [True, False, True, None],
        'col5': ['x', '', 'z', 'a'],
        'col6': [6, None, 8, 9],
        'col7': [None, None, None, None],
        'col8': ['', '', '', ''],
        'col9': ['test1', 'test2', 'test3', 'test4'],
        'col10': [10, 20, 30, 40],
        'col11': [None, 'b', None, 'd'],
        'col12': [12.1, None, 12.3, 12.4],
        'col13': [True, True, False, False],
        'col14': ['', 'b', 'c', 'd'],
        'col15': [15, 15, 15, 15],
        'col16': [None, None, None, None],
        'col17': ['a', 'b', 'c', 'd'],
        'col18': [18, 19, 20, 21],
        'col19': [None, 'y', None, 'z'],
        'col20': [20, 21, 22, 23]
        }
        self.df = pd.DataFrame(data)

    def test_slicing_issue_old_method(self):
        print("Testing with current stream_upload method...")
        try:
            dataset_old = self.domo.ds_create(self.df,'TEST_SLICING_ISSUE_OLD', 'Test dataset for slicing issue in PyDomo SDK (old method)')
            self.domo.ds_update(dataset_old, self.df)
            print("Old method succeeded.")
        except Exception as e:
            self.fail(f"Old method failed with error: {e}")

    def test_slicing_issue_new_method(self):
        print("Testing revised stream_upload method...")
        try:
            self.domo.utilities.stream_upload = self.domo.utilities.stream_upload_new
            dataset_new = self.domo.ds_create(self.df,'TEST_SLICING_ISSUE_NEW', 'Test dataset for slicing issue in PyDomo SDK (new method)')
            self.domo.ds_update(dataset_new, self.df)
            print("New method succeeded.")
        except Exception as e:
            self.fail(f"New method failed with error: {e}")

if __name__ == '__main__':
    unittest.main()