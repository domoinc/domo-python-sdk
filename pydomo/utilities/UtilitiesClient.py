
import io
import os
import requests
import json

import pandas as pd

from pydomo.DomoAPIClient import DomoAPIClient
from pydomo.Transport import HTTPMethod
from pydomo.datasets import DataSetClient

#from pydomo import Domo
#dd = Domo('f537bdaf-2ecb-41bf-a2ff-26351f9cac3f','6b46c0fd7bf2f413f80e2637fd009babc06359dd590af49ba7a30ca9ea72b19d')
#aa = dd.ds_get('77f0768d-5a4d-43c8-bbb4-0b30c83d2233')
#dd.utilities.typeConversionText( dict(aa.dtypes)['Date Column'])

class UtilitiesClient(DomoAPIClient):
    def __init__(self, transport, logger):
        super(UtilitiesClient, self).__init__(transport, logger)
        self.ds = DataSetClient(self.transport, self.logger)

    def domo_schema(self, ds_id):
        this_get = self.ds.get(ds_id)
        return this_get['schema']['columns']

    def data_schema(self, df):
        col_types = dict(df.dtypes)
        output_list = []
        for key, value in col_types.items():
            output_list.append({'type': self.typeConversionText(value), 'name': key})
        return output_list

    def typeConversionText(self, dt):
        result = 'STRING'
        if dt == '<M8[ns]':
            result = 'DATETIME'
        if dt == 'int64':
            result = 'LONG'
        if dt == 'float64':
            result = 'DOUBLE'

        return result