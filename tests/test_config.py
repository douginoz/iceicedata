import json
import os
import sys

def load_config(config_file):
    if not os.path.isfile(config_file):
        print(f"Config file {config_file} not found. Example config file format:")
        print(json.dumps({
            "mqtt_server": "mqtt.example.com",
            "mqtt_port": 1883,
            "mqtt_user": "username",
            "mqtt_password": "password",
            "mqtt_root": "RootTopic/",
            "mqtt_windrose_root": "WindroseTopic/"
        }, indent=2))
        sys.exit(1)
    
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    return config

def save_mqtt_config(config_file):
    if os.path.isfile(config_file):
        config = load_config(config_file)
    else:
        config = {}

    config["mqtt_server"] = input(f"Enter MQTT server (default: {config.get('mqtt_server', 'mqtt.example.com')}): ") or config.get("mqtt_server", "mqtt.example.com")
    config["mqtt_port"] = int(input(f"Enter MQTT port (default: {config.get('mqtt_port', 1883)}): ") or config.get("mqtt_port", 1883))
    config["mqtt_user"] = input(f"Enter MQTT user (default: {config.get('mqtt_user', 'username')}): ") or config.get("mqtt_user", "username")
    config["mqtt_password"] = input(f"Enter MQTT password (default: {config.get('mqtt_password', 'password')}): ") or config.get("mqtt_password", "password")
    config["mqtt_root"] = input(f"Enter MQTT root topic (default: {config.get('mqtt_root', 'RootTopic/')}): ") or config.get("mqtt_root", "RootTopic/")
    if not config["mqtt_root"].endswith('/'):
        config["mqtt_root"] += '/'
    config["mqtt_windrose_root"] = input(f"Enter MQTT windrose root topic (default: {config.get('mqtt_windrose_root', 'WindroseTopic/')}): ") or config.get("mqtt_windrose_root", "WindroseTopic/")
    if not config["mqtt_windrose_root"].endswith('/'):
        config["mqtt_windrose_root"] += '/'

    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    print(f"Configuration saved to {config_file}")
