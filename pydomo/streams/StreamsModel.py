from ..common import DomoObject


class CreateStreamRequest(DomoObject):
    accepted_attrs = [
        'dataSet',
        'updateMethod'
    ]
    def __init__(self, data_set_request, update_method):
        super().__init__()
        self.dataSet = data_set_request
        self.updateMethod = update_method


class UpdateMethod:
    APPEND = 'APPEND'
    REPLACE = 'REPLACE'
