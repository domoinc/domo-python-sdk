from pydomo.datasets.DataSetModel import DataSet


class Stream:
    def __init__(self):
        self.id = 0
        self.dataSet = DataSet()
        self.updateMethod = ''
        self.createdAt = ''
        self.modifiedAt = ''


class CreateStreamRequest:
    def __init__(self, data_set_request, update_method):
        self.dataSet = data_set_request
        self.updateMethod = update_method


class Execution:
    def __init__(self):
        self.id = 0
        self.startedAt = ''
        self.currentState = ''
        self.createdAt = ''
        self.modifiedAt = ''


class UpdateMethod:
    APPEND = 'APPEND'
    REPLACE = 'REPLACE'
