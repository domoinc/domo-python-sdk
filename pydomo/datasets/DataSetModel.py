class Column:
    def __init__(self, column_type, name):
        self.type = column_type
        self.name = name


class ColumnType:
    STRING = 'STRING'
    DECIMAL = 'DECIMAL'
    LONG = 'LONG'
    DOUBLE = 'DOUBLE'
    DATE = 'DATE'
    DATETIME = 'DATETIME'


class DataSetRequest:
    def __init__(self):
        self.name = ''
        self.description = ''
        self.schema = ''


class DataSet:
    def __init__(self):
        self.id = 0
        self.name = ''
        self.description = ''
        self.rows = 0
        self.columns = 0
        self.schema = Schema([])
        self.owner = Owner()
        self.createdAt = ''
        self.updatedAt = ''


class DataSetAndPDP(DataSet):
    def __init__(self):
        super().__init__()
        self.pdpEnabled = False
        self.policies = []


class DataSetListResult:
    def __init__(self):
        self.id = 0
        self.name = ''
        self.description = ''
        self.rows = 0
        self.columns = 0
        self.owner = Owner()
        self.dataCurrentAt = ''
        self.createdAt = ''
        self.updatedAt = ''
        self.pdpEnabled = False


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


class Owner:
    def __init__(self):
        self.id = 0
        self.name = ''


class Policy:
    def __init__(self):
        self.id = 0
        self.type = ''
        self.name = ''
        self.filters = []
        self.users = []
        self.groups = []


class PolicyType:
    USER = 'user'
    SYSTEM = 'system'


class PolicyFilter:
    def __init__(self):
        self.column = ''
        self.values = []
        self.operator = ''
        self.NOT = False


class Schema:
    def __init__(self, columns):
        self.columns = columns
