import json
import os
import sys
import yaml

def load_config(config_file):
    if not os.path.isfile(config_file):
        print(f"Error: Configuration file '{config_file}' not found. Please use the '-S' option to set up a new configuration or provide an existing configuration file with the '-m' option.")
        sys.exit(1)
    
    with open(config_file, 'r') as f:
        config = json.load(f) if config_file.endswith('.json') else yaml.safe_load(f)
    
    config["debug"] = config.get("debug", False)
    return config

def validate_config(config):
    required_keys = ["mqtt_server", "mqtt_port", "mqtt_user", "mqtt_password", "mqtt_root", "mqtt_windrose_root"]
    for key in required_keys:
        if key not in config:
            return False
    return True
