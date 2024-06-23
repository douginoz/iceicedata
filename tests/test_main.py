import unittest
from unittest.mock import patch, MagicMock
from iceicedata.main import main

class TestMain(unittest.TestCase):
    @patch('iceicedata.selenium_utils.initialize_driver')
    @patch('iceicedata.selenium_utils.validate_url')
    @patch('iceicedata.selenium_utils.extract_coordinates')
    @patch('iceicedata.selenium_utils.get_station_id_from_url')
    @patch('iceicedata.selenium_utils.get_placemarkers')
    @patch('iceicedata.selenium_utils.select_placemarker')
    @patch('iceicedata.selenium_utils.get_station_id')
    @patch('iceicedata.data_processing.process_station_data')
    @patch('iceicedata.mqtt_utils.publish_to_mqtt')
    def test_main_function(self, mock_publish_to_mqtt, mock_process_station_data, mock_get_station_id, mock_select_placemarker, mock_get_placemarkers, mock_get_station_id_from_url, mock_extract_coordinates, mock_validate_url, mock_initialize_driver):
        # Set up mock return values
        mock_initialize_driver.return_value = MagicMock()
        mock_validate_url.return_value = 'valid_url'
        mock_extract_coordinates.return_value = ('latitude', 'longitude', 'zoom')
        mock_get_station_id_from_url.return_value = None
        mock_get_placemarkers.return_value = (['title1'], [MagicMock()])
        mock_select_placemarker.return_value = 0
        mock_get_station_id.return_value = 'station_id'
        mock_process_station_data.return_value = ('data', 'wind_data', 'station_identifier')

        # Call the main function with test parameters
        main(url='test_url', json_file='test.json', output_file='test_output.txt', mqtt_config='test_config.json', windrose_topic='test_topic')

        # Assert that the mocked functions were called as expected
        mock_initialize_driver.assert_called_once()
        mock_validate_url.assert_called_once_with('test_url')
        mock_extract_coordinates.assert_called_once_with('valid_url')
        mock_get_station_id_from_url.assert_called_once_with('valid_url')
        mock_get_placemarkers.assert_called_once()
        mock_select_placemarker.assert_called_once_with(['title1'])
        mock_get_station_id.assert_called_once()
        mock_process_station_data.assert_called_once()
        mock_publish_to_mqtt.assert_called_once()

if __name__ == '__main__':
    unittest.main()
