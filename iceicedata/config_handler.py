import yaml
import sys
import os

DEFAULT_CONFIG = {
    "mqtt_server": "",
    "mqtt_port": 1883,
    "mqtt_user": "",
    "mqtt_password": "",
    "mqtt_root": "",
    "mqtt_windrose_root": "",
    "mqtt_retain": False
}

def load_config(config_file):
    if not os.path.isfile(config_file):
        return None

    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)

    return config

def save_mqtt_config(config_file):
    config = load_config(config_file) or {}

    config["mqtt_server"] = input(f"Enter MQTT server (default: {config.get('mqtt_server', 'mqtt.example.com')}): ") or config.get("mqtt_server", "mqtt.example.com")
    config["mqtt_port"] = int(input(f"Enter MQTT port (default: {config.get('mqtt_port', 1883)}): ") or config.get("mqtt_port", 1883))
    config["mqtt_user"] = input(f"Enter MQTT user (default: {config.get('mqtt_user', '')}): ") or config.get("mqtt_user", "")
    config["mqtt_password"] = input(f"Enter MQTT password (default: {config.get('mqtt_password', '')}): ") or config.get("mqtt_password", "")
    config["mqtt_root"] = input(f"Enter MQTT root topic (default: {config.get('mqtt_root', 'RootTopic/')}): ") or config.get("mqtt_root", "RootTopic/")
    if not config["mqtt_root"].endswith('/'):
        config["mqtt_root"] += '/'
    config["mqtt_windrose_root"] = input(f"Enter MQTT windrose root topic (default: {config.get('mqtt_windrose_root', '')}): ") or config.get("mqtt_windrose_root", "")
    if not config["mqtt_windrose_root"].endswith('/'):
        config["mqtt_windrose_root"] += '/'
    config["mqtt_retain"] = input(f"Set retain flag (default: {config.get('mqtt_retain', False)}): ") or config.get("mqtt_retain", False)
    config["mqtt_retain"] = str(config["mqtt_retain"]).lower() in ['true', '1', 't', 'y', 'yes']

    with open(config_file, 'w') as f:
        yaml.safe_dump(config, f, default_flow_style=False)
    print(f"Configuration saved to {config_file}")

def validate_config(config):
    required_keys = ["mqtt_server", "mqtt_port", "mqtt_user", "mqtt_password", "mqtt_root", "mqtt_windrose_root"]
    for key in required_keys:
        if key not in config:
            return False
    return True
