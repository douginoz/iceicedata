import json
import os
import sys
import paho.mqtt.client as mqtt

def load_config(config_file):
    if not os.path.isfile(config_file):
        print(f"Config file {config_file} not found. Example config file format:")
        print(json.dumps({
            "mqtt_server": "mqtt.example.com",
            "mqtt_port": 1883,
            "mqtt_user": "username",
            "mqtt_password": "password",
            "mqtt_root": "RootTopic/",
            "mqtt_windrose_root": "WindroseTopic/",
            "mqtt_retain": False
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

def send_mqtt_data(data, config, topic):
    print("Sending data to MQTT server with topic:", topic)
    client = mqtt.Client()
    if config["mqtt_user"] and config["mqtt_password"]:
        client.username_pw_set(config["mqtt_user"], config["mqtt_password"])

    def on_connect(client, userdata, flags, rc):
        pass

    def on_publish(client, userdata, mid):
        pass

    client.on_connect = on_connect
    client.on_publish = on_publish

    try:
        client.connect(config["mqtt_server"], config["mqtt_port"], 60)
        client.loop_start()
        result = client.publish(topic, json.dumps(data), retain=config.get("mqtt_retain", True))
        result.wait_for_publish()
        client.loop_stop()
        client.disconnect()
        print("Data published to MQTT server.")
    except Exception as e:
        print(f"An error occurred while publishing to MQTT: {e}")
        print(f"An error occurred while publishing to MQTT: {e}")

    if not config.get('mqtt_retain'):
        print("MQTT retain flag is not set in the configuration file. Please add it to the configuration file and try again.")
