import json
import os

DEFAULT_CONFIG = {
    "mqtt_server": "",
    "mqtt_port": 1883,
    "mqtt_user": "",
    "mqtt_password": "",
    "mqtt_root": "",
    "mqtt_windrose_root": ""
}

CONFIG_COMMENTS = """
{
    // Configuration file for the iceicedata program
    // MQTT server address
    "mqtt_server": "",
    // MQTT server port
    "mqtt_port": 1883,
    // MQTT username
    "mqtt_user": "",
    // MQTT password
    "mqtt_password": "",
    // Root topic for MQTT
    "mqtt_root": "",
    // Root topic for windrose data
    "mqtt_windrose_root": ""
}
"""

def create_default_config(config_file):
    with open(config_file, 'w') as f:
        f.write(CONFIG_COMMENTS)

def load_config(config_file):
    if not os.path.isfile(config_file):
        create_default_config(config_file)
        print(f"Default configuration file created at {config_file}. Please update it with your MQTT settings.")
        sys.exit(1)

    with open(config_file, 'r') as f:
        config = json.load(f)

    return config

def validate_config(config):
    required_keys = ["mqtt_server", "mqtt_port", "mqtt_user", "mqtt_password", "mqtt_root", "mqtt_windrose_root"]
    for key in required_keys:
        if key not in config:
            return False
    return True
