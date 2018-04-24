import unittest
from transport.data_provider import DataProvider


class DataProviderTest(unittest.TestCase):
    def setUp(self):
        self.classObj = DataProvider('TOKEN', '', '/', 'manual')

    def test_invalid_token_input(self):
        with self.assertRaises(AssertionError):
            self.classObj = DataProvider('')

    def test_invalid_token_type(self):
        with self.assertRaises(TypeError):
            self.classObj = DataProvider(1)

    def test_invalid_download_path_type(self):
        with self.assertRaises(AssertionError):
            self.classObj = DataProvider('TOKEN', 1)

    def test_invalid_working_directory_type(self):
        with self.assertRaises(AttributeError):
            self.classObj = DataProvider('TOKEN', '', 1)

    def test_invalid_working_directory_input(self):
        with self.assertRaises(AssertionError):
            self.classObj = DataProvider('TOKEN', '', 'invalid')

    def test_invalid_mode_type(self):
        with self.assertRaises(AssertionError):
            self.classObj = DataProvider('TOKEN', '', '/valid', 1)

    def test_invalid_mode_input(self):
        with self.assertRaises(AssertionError):
            self.classObj = DataProvider('TOKEN', '', '/valid', 'invalid')

    def test_invalid_changing_download_path_type(self):
        with self.assertRaises(TypeError):
            self.classObj.download_path = 1

    def test_invalid_changing_working_directory_type(self):
        with self.assertRaises(TypeError):
            self.classObj.working_directory = 1

    def test_invalid_changing_working_directory_input(self):
        with self.assertRaises(ValueError):
            self.classObj.working_directory = 'invalid string'

    def test_invalid_changing_mode_type(self):
        with self.assertRaises(TypeError):
            self.classObj.mode = 1

    def test_invalid_changing_mode_input(self):
        with self.assertRaises(ValueError):
            self.classObj.mode = 'invalid'


if __name__ == "__main__":
    unittest.main()
