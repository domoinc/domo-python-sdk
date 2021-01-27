from ..common import DomoObject


class Column(DomoObject):
    accepted_attrs = [
        'type',
        'name'
    ]

    def __init__(self, column_type, name):
        super().__init__()
        self.type = column_type
        self.name = name


class ColumnType:
    STRING = 'STRING'
    DECIMAL = 'DECIMAL'
    LONG = 'LONG'
    DOUBLE = 'DOUBLE'
    DATE = 'DATE'
    DATETIME = 'DATETIME'


class DataSetRequest(DomoObject):
    accepted_attrs = [
        'name',
        'description',
        'schema'
    ]


class FilterOperator:
    EQUALS = 'EQUALS'
    LIKE = 'LIKE'
    GREATER_THAN = 'GREATER_THAN'
    LESS_THAN = 'LESS_THAN'
    GREATER_THAN_EQUAL = 'GREATER_THAN_EQUAL'
    LESS_THAN_EQUAL = 'LESS_THAN_EQUAL'
    BETWEEN = 'BETWEEN'
    BEGINS_WITH = 'BEGINS_WITH'
    ENDS_WITH = 'ENDS_WITH'
    CONTAINS = 'CONTAINS'


class Policy(DomoObject):
    accepted_attrs = [
        'id',
        'type',
        'name',
        'filters',
        'users',
        'virtualUsers',
        'groups'
    ]


class PolicyType:
    USER = 'user'
    SYSTEM = 'system'


class PolicyFilter(DomoObject):
    accepted_attrs = [
        'column',
        'values',
        'operator',
        'not'
    ]


class Schema(DomoObject):
    accepted_attrs = [
        'columns'
    ]
    def __init__(self, columns):
        self.columns = columns


class Sorting:
    CARD_COUNT = 'cardCount'
    DEFAULT = None
    NAME = 'name'
    STATUS = 'errorState'
    UPDATED = 'lastUpdated'


class UpdateMethod:
    APPEND = 'APPEND'
    REPLACE = 'REPLACE'
