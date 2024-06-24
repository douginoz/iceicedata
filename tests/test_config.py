import unittest
from unittest.mock import patch, mock_open, call
from iceicedata.config import load_config, save_mqtt_config
import yaml

class TestConfig(unittest.TestCase):
    @patch('os.path.isfile', return_value=True)
    @patch('builtins.open', new_callable=mock_open, read_data='mqtt_server: test_server')
    def test_load_config(self, mock_file, mock_isfile):
        config = load_config('test_config.yaml')
        self.assertEqual(config['mqtt_server'], 'test_server')

    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.isfile', return_value=True)
    @patch('iceicedata.config.load_config', return_value={'mqtt_server': 'test_server', 'mqtt_port': 1883, 'mqtt_user': 'username', 'mqtt_password': 'password', 'mqtt_root': 'RootTopic/', 'mqtt_windrose_root': 'WindroseTopic/'})
    def test_save_mqtt_config(self, mock_load_config, mock_isfile, mock_file):
        input_values = ['test_server', '1883', 'username', 'password', 'RootTopic/', 'WindroseTopic/']
        with patch('builtins.input', side_effect=input_values):
            save_mqtt_config('test_config.yaml')
        expected_calls = [
            call('{'),
            call('\n  '),
            call('"mqtt_server"'),
            call(': '),
            call('"test_server"'),
            call(',\n  '),
            call('"mqtt_port"'),
            call(': '),
            call('1883'),
            call(',\n  '),
            call('"mqtt_user"'),
            call(': '),
            call('"username"'),
            call(',\n  '),
            call('"mqtt_password"'),
            call(': '),
            call('"password"'),
            call(',\n  '),
            call('"mqtt_root"'),
            call(': '),
            call('"RootTopic/"'),
            call(',\n  '),
            call('"mqtt_windrose_root"'),
            call(': '),
            call('"WindroseTopic/"'),
            call('\n'),
            call('}')
        ]
        mock_file().write.assert_called()

if __name__ == '__main__':
    unittest.main()
