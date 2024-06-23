import paho.mqtt.client as mqtt
from iceicedata.config import load_config

def publish_to_mqtt(mqtt_config, json_data, wind_data, station_identifier, windrose_topic):
    config = load_config(mqtt_config)
    client = mqtt.Client()
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

        topic = f"{config['mqtt_root']}{station_identifier}"
        result = client.publish(topic, json_data, retain=True)
        result.wait_for_publish()

        if windrose_topic:
            windrose_topic_name = windrose_topic if isinstance(windrose_topic, str) else config.get("mqtt_windrose_root")
            if windrose_topic_name:
                windrose_result = client.publish(windrose_topic_name, json_data, retain=True)
                windrose_result.wait_for_publish()
            else:
                print("Windrose topic name not provided and not found in the config file.")

        client.loop_stop()
        client.disconnect()

    except Exception as e:
        print(f"An error occurred while publishing to MQTT: {e}")
