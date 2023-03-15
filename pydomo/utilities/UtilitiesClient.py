
import json
import math
import sys
import json

from pydomo.DomoAPIClient import DomoAPIClient
from pydomo.datasets import DataSetClient
from pydomo.streams import StreamClient

class UtilitiesClient(DomoAPIClient):
    def __init__(self, transport, logger):
        super(UtilitiesClient, self).__init__(transport, logger)
        self.ds = DataSetClient(self.transport, self.logger)
        self.stream = StreamClient(self.transport, self.logger)
        self.transport = transport

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

    def identical(self, c1, c2):
        cc1 = json.dumps(c1)
        cc2 = json.dumps(c2)
        return cc1 == cc2

    def get_stream_id(self, ds_id):
        url = '/v1/streams/search?q=dataSource.id:{ds_id}'.format(ds_id=ds_id)
        all_info = self._get(url,'Search to retrieve stream id')
        return all_info[0]['id']

    def estimate_chunk_rows(self, data, kbytes=10000):
        sz = sys.getsizeof(data)
        targetSize = kbytes * 3 # compression factor
        data_rows = len(data.index)
        ch_size = data_rows
        if sz / 1000 > targetSize:
            ch_size = math.floor(data_rows*(targetSize) / (sz/1000))
        return(ch_size)

    def stream_upload(self, ds_id, df_up, warn_schema_change=True):
        domoSchema = self.domo_schema(ds_id)
        dataSchema = self.data_schema(df_up)

        stream_id = self.get_stream_id(ds_id)

        if self.identical(domoSchema,dataSchema) == False:
            new_schema = {'schema': {'columns': dataSchema}}
            url = '/v1/datasets/{ds}'.format(ds=ds_id)
            change_result = self.transport.put(url,new_schema)
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

        for i in range(math.ceil(df_rows/chunksz)):
            df_sub = df_up.iloc[start:end, ]
            csv = df_sub.to_csv(header=False,index=False)
            self.stream.upload_part(stream_id, exec_id, start, csv)
            start = end
            end = end + chunksz
            if end > df_rows:
                end = df_rows

        result = self.stream.commit_execution(stream_id, exec_id)

        return result

    def stream_create(self, up_ds, name, description, updateMethod='REPLACE', keyColumnNames=[]):
        df_schema = self.data_schema(up_ds)
        req_body = {'dataSet': {'name': name, 'description': description, 'schema': {'columns': df_schema}}, 'updateMethod': updateMethod}
        if( updateMethod == 'UPSERT' ):
            req_body['keyColumnNames'] = keyColumnNames
        # return req_body
        st_created = self.transport.post('/v1/streams/', req_body, {})
        return json.loads(st_created.content.decode('utf-8'))