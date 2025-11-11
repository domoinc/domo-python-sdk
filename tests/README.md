# Tests

This directory contains unit tests for the PyDomo SDK. The commands below must be run from the root of the project directory.

## Running Tests

### Run all tests
```bash
python -m unittest discover tests
```

### Run a specific test file
```bash
python -m unittest tests.test_utilities_type_conversion -v
```

### Run a specific test class
```bash
python -m unittest tests.test_utilities_type_conversion.TestUtilitiesTypeConversion -v
```

### Run a specific test method
```bash
python -m unittest tests.test_utilities_type_conversion.TestUtilitiesTypeConversion.test_datetime_types -v
```