from pydomo import Domo
import logging

from pydomo.tests.DataSetIT import DataSetTestSuite
from pydomo.tests.UsersIT import UserTestSuite


def init_client():
    client_id = 'b1a9de69-232d-485b-8f73-1351b098283b'
    client_secret = '82184c91164d7cba5c727a67f3f4ac53af62949912e1705e560cc1b880638bde'
    api_host = 'api.domo.com'
    use_https = True
    logger_name = ''
    logger_level = logging.INFO
    return Domo(client_id, client_secret, api_host, use_https, logger_name, logger_level)


def run_all():
    domo = init_client()
    #UserTestSuite(domo).run_all()
    DataSetTestSuite(domo).run_all()

run_all()
