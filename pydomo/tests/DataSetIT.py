from pydomo.datasets import Column
from pydomo.datasets import ColumnType
from pydomo.datasets import DataSetRequest
from pydomo.datasets import Schema


class DataSetTestSuite:
    def __init__(self, domo):
        self.domo = domo
        self.logger = self.domo.logger
        self.shouldHaveFailed = "!!!!!!!!!!!!!!!!!!!!!!!! THIS TEST SHOULD HAVE FAILED !!!!!!!!!!!!!!!!!!!!!!!!"

    def run_all(self):
        self.csv_commas()

    def csv_commas(self):
        datasets = self.domo.datasets

        # Define a DataSet Schema
        dsr = DataSetRequest()
        dsr.name = 'Leonhard Euler Party'
        dsr.description = 'Mathematician Guest List'
        dsr.schema = Schema([Column(ColumnType.STRING, 'Friend'), Column(ColumnType.STRING, 'Attending')])

        # Create a DataSet with the given Schema
        dataset = datasets.create(dsr)
        self.logger.info("Created DataSet " + str(dataset.id))

        # Import Data from a file
        csv_file_path = './math2.csv'
        datasets.data_import_from_file(dataset.id, csv_file_path)
        self.logger.info("Uploaded data from a file to DataSet " + str(dataset.id))

        # Export Data to a file (also returns the readable/writable file object)
        csv_file_path = './returnedMathematicians.csv'
        include_csv_header = True
        csv_file = datasets.data_export_to_file(dataset.id, csv_file_path, include_csv_header)
        csv_file.close()
        self.logger.info("Downloaded data as a file from DataSet " + str(dataset.id))