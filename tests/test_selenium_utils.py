import unittest
from unittest.mock import MagicMock, patch
from iceicedata.selenium_utils import get_station_id

class TestSeleniumUtils(unittest.TestCase):

    def test_validate_url(self):
        self.assertEqual(validate_url('https://tempestwx.com/map/12345'), 'https://tempestwx.com/map/12345')
        with self.assertRaises(ValueError):
            validate_url('invalid_url')

    def test_extract_coordinates(self):
        self.assertEqual(extract_coordinates('https://tempestwx.com/map/50515/65.1557/-16.47/6'), ('65.1557', '-16.47', '6'))
        with self.assertRaises(ValueError):
            extract_coordinates('invalid_url')

    @patch('iceicedata.selenium_utils.webdriver.Firefox')
    def test_get_station_id_from_url(self, mock_firefox):
        self.assertEqual(get_station_id_from_url('https://tempestwx.com/map/12345'), '12345')
        self.assertIsNone(get_station_id_from_url('invalid_url'))

    # Other functions can be tested similarly...

if __name__ == '__main__':
    unittest.main()
