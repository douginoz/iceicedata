import json
import os
import sys
import logging
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

def send_mqtt_data(data, config, topic):
    logger = logging.getLogger()
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
        logger.debug("Connecting to MQTT server: %s:%s", config["mqtt_server"], config["mqtt_port"])
        client.connect(config["mqtt_server"], config["mqtt_port"], 60)
        client.loop_start()
        result = client.publish(topic, json.dumps(data), retain=config.get("mqtt_retain", False))
        result.wait_for_publish()
        client.loop_stop()
        client.disconnect()
    except Exception as e:
        logger.error("An error occurred while publishing to MQTT: %s", e)
        print(f"An error occurred while publishing to MQTT: {e}")