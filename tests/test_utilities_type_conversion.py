import unittest
import pandas as pd
import numpy as np
from unittest.mock import Mock
from pydomo.utilities.UtilitiesClient import UtilitiesClient


class TestUtilitiesTypeConversion(unittest.TestCase):

    def setUp(self):
        self.mock_transport = Mock()
        self.mock_logger = Mock()
        self.client = UtilitiesClient(self.mock_transport, self.mock_logger)

    def test_datetime_types(self):
        datetime_types = [
            np.dtype('datetime64[ns]'),
            np.dtype('datetime64[us]'),
            np.dtype('datetime64[ms]'),
            np.dtype('datetime64[s]'),
        ]

        for dt in datetime_types:
            result = self.client.type_conversion_text(dt)
            self.assertEqual(result, 'DATETIME',
                           f'Failed for dtype: {dt}')

    def test_integer_types(self):
        integer_types = [
            np.dtype('int8'),
            np.dtype('int16'),
            np.dtype('int32'),
            np.dtype('int64'),
            np.dtype('uint8'),
            np.dtype('uint16'),
            np.dtype('uint32'),
            np.dtype('uint64'),
            pd.Int8Dtype(),
            pd.Int16Dtype(),
            pd.Int32Dtype(),
            pd.Int64Dtype(),
        ]

        for dt in integer_types:
            result = self.client.type_conversion_text(dt)
            self.assertEqual(result, 'LONG',
                           f'Failed for dtype: {dt}')

    def test_float_types(self):
        float_types = [
            np.dtype('float16'),
            np.dtype('float32'),
            np.dtype('float64'),
            pd.Float32Dtype(),
            pd.Float64Dtype(),
        ]

        for dt in float_types:
            result = self.client.type_conversion_text(dt)
            self.assertEqual(result, 'DOUBLE',
                           f'Failed for dtype: {dt}')

    def test_string_types(self):
        string_types = [
            np.dtype('object'),
            np.dtype('U10'),  # Unicode string
            pd.StringDtype(),
        ]

        for dt in string_types:
            result = self.client.type_conversion_text(dt)
            self.assertEqual(result, 'STRING',
                           f'Failed for dtype: {dt}')

    def test_bool_type_defaults_to_string(self):
        result = self.client.type_conversion_text(np.dtype('bool'))
        self.assertEqual(result, 'STRING')

    def test_data_schema_with_mixed_types(self):
        df = pd.DataFrame({
            'int_col': pd.array([1, 2, 3], dtype='Int64'),
            'float_col': pd.array([1.1, 2.2, 3.3], dtype='Float64'),
            'string_col': pd.array(['a', 'b', 'c'], dtype='string'),
            'datetime_col': pd.to_datetime(['2024-01-01', '2024-01-02', '2024-01-03']),
        })

        schema = self.client.data_schema(df)

        self.assertEqual(len(schema), 4)

        schema_map = {col['name']: col['type'] for col in schema}

        self.assertEqual(schema_map['int_col'], 'LONG')
        self.assertEqual(schema_map['float_col'], 'DOUBLE')
        self.assertEqual(schema_map['string_col'], 'STRING')
        self.assertEqual(schema_map['datetime_col'], 'DATETIME')

    def test_data_schema_with_numpy_types(self):
        df = pd.DataFrame({
            'np_int': np.array([1, 2, 3], dtype=np.int64),
            'np_float': np.array([1.1, 2.2, 3.3], dtype=np.float64),
            'np_str': np.array(['x', 'y', 'z'], dtype=object),
        })

        schema = self.client.data_schema(df)

        self.assertEqual(len(schema), 3)

        schema_map = {col['name']: col['type'] for col in schema}

        self.assertEqual(schema_map['np_int'], 'LONG')
        self.assertEqual(schema_map['np_float'], 'DOUBLE')
        self.assertEqual(schema_map['np_str'], 'STRING')

    def test_data_schema_preserves_column_names(self):
        df = pd.DataFrame({
            'Column With Spaces': [1, 2, 3],
            'CamelCaseColumn': [4.5, 5.5, 6.5],
            'column_with_underscores': ['a', 'b', 'c'],
        })

        schema = self.client.data_schema(df)
        column_names = [col['name'] for col in schema]

        self.assertIn('Column With Spaces', column_names)
        self.assertIn('CamelCaseColumn', column_names)
        self.assertIn('column_with_underscores', column_names)

    def test_empty_dataframe(self):
        df = pd.DataFrame({
            'int_col': pd.array([], dtype='Int64'),
            'string_col': pd.array([], dtype='string'),
        })

        schema = self.client.data_schema(df)

        self.assertEqual(len(schema), 2)
        schema_map = {col['name']: col['type'] for col in schema}

        self.assertEqual(schema_map['int_col'], 'LONG')
        self.assertEqual(schema_map['string_col'], 'STRING')

    def test_type_conversion_with_string_input(self):
        test_cases = {
            'int64': 'LONG',
            'float64': 'DOUBLE',
            'datetime64[ns]': 'DATETIME',
            'object': 'STRING',
            'Int32': 'LONG',
            'Float64': 'DOUBLE',
            'some_unknown_type': 'STRING',  # Should default to STRING
        }

        for input_str, expected_output in test_cases.items():
            result = self.client.type_conversion_text(input_str)
            self.assertEqual(result, expected_output,
                           f'Failed for string input: {input_str}')


if __name__ == '__main__':
    unittest.main()