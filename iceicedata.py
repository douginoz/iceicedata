import json
import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import paho.mqtt.client as mqtt
import time
import os
import sys
from datetime import datetime
import pytz

# Helper functions
def convert_wind_speed_to_mps(speed):
    try:
        return round(float(speed) * 0.27778, 2)
    except ValueError:
        return speed  # Return the original speed if conversion fails

def split_value_and_unit(value):
    parts = value.split(' ')
    numeric_value = parts[0]
    unit = ' '.join(parts[1:]) if len(parts) > 1 else None
    return numeric_value, unit

def convert_timestamp_to_unix_ms(timestamp_str, timezone_str):
    try:
        local_tz = pytz.timezone(timezone_str)
        local_dt = datetime.strptime(timestamp_str, '%m/%d/%Y %I:%M:%S %p')
        local_dt = local_tz.localize(local_dt, is_dst=None)
        unix_time_ms = int(local_dt.timestamp() * 1000)
        return unix_time_ms
    except Exception as e:
        return None

def convert_compass_to_degrees(direction):
    compass_to_degrees = {
        "N": 0, "NNE": 22.5, "NE": 45, "ENE": 67.5,
        "E": 90, "ESE": 112.5, "SE": 135, "SSE": 157.5,
        "S": 180, "SSW": 202.5, "SW": 225, "WSW": 247.5,
        "W": 270, "WNW": 292.5, "NW": 315, "NNW": 337.5
    }
    return compass_to_degrees.get(direction, None)

def validate_url(url):
    if "tempestwx.com/map/" not in url:
        raise ValueError("Invalid URL format. Please provide a valid TempestWX URL.")
    return url

def extract_coordinates(url):
    parts = url.split('/')
    if len(parts) >= 7:
        latitude = parts[-3]
        longitude = parts[-2]
        zoom = parts[-1]
        return latitude, longitude, zoom
    else:
        raise ValueError("URL does not contain valid coordinates.")

def get_station_id_from_url(url):
    parts = url.split('/')
    if len(parts) >= 7 and parts[-4].isdigit():
        return parts[-4]
    return None

def get_placemarkers(url):
    try:
        # Open the target webpage
        driver.get(url)
        time.sleep(5)  # Wait for page to fully load

        # Wait for the map to load
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div[title]'))
        )
        
        # Find all placemarkers with a title attribute
        placemarkers = driver.find_elements(By.CSS_SELECTOR, 'div[title]')
        
        if len(placemarkers) > 50:
            print("Too many markers found. Please zoom in closer and try again.")
            return [], []

        # Extract the title of each placemarker
        placemarker_titles = [placemarker.get_attribute('title').strip() for placemarker in placemarkers]
        
        return placemarker_titles, placemarkers

    except Exception as e:
        print(f"An error occurred while getting placemarkers: {e}")
        return [], []

def select_placemarker(placemarker_titles):
    if len(placemarker_titles) == 1:
        print(f"Only one placemarker found: {placemarker_titles[0]}")
        return 0
    elif len(placemarker_titles) == 0:
        print("No placemarkers found.")
        return -1
    else:
        print("Multiple placemarkers found:")
        for idx, title in enumerate(placemarker_titles):
            print(f"{idx + 1}: {title}")
        while True:
            try:
                selection = int(input("Enter the number of the placemarker you want to select: ")) - 1
                if 0 <= selection < len(placemarker_titles):
                    return selection
                else:
                    print(f"Please enter a number between 1 and {len(placemarker_titles)}.")
            except ValueError:
                print("Please enter a valid number.")

def get_station_id(placemarker):
    try:
        placemarker.click()
        time.sleep(5)  # Wait for click action to take effect
        
        # Wait for the station-detail element to appear
        station_detail = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.ID, 'station-detail'))
        )
        
        # Extract the station ID from the href attribute
        station_info = station_detail.find_element(By.XPATH, './/a[contains(@href, "/station/")]')
        station_id = station_info.get_attribute('href').split('/station/')[1].split('?')[0]
        return station_id
    except Exception as e:
        print(f"An error occurred while getting the station ID: {e}")
        return None

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

def main(url=None, json_file=None, output_file=None, mqtt_config=None, windrose_topic=None):
    global driver
    driver = None
    
    try:
        if not url:
            return
        
        # Initialize the WebDriver
        service = Service('/usr/local/bin/geckodriver')
        options = webdriver.FirefoxOptions()
        options.add_argument('--headless')
        driver = webdriver.Firefox(service=service, options=options)
        
        # Validate and extract details from the URL
        final_url = validate_url(url)
        latitude, longitude, zoom = extract_coordinates(final_url)
        station_id = get_station_id_from_url(final_url)
        
        if not station_id:
            # Get all placemarkers
            placemarker_titles, placemarkers = get_placemarkers(final_url)
            if not placemarkers:
                return
            
            # Select a placemarker
            selection = select_placemarker(placemarker_titles)
            if selection == -1:
                return
            
            # Get the station ID
            station_id = get_station_id(placemarkers[selection])
            if not station_id:
                print("Failed to retrieve the station ID.")
                return
        
        # Construct the URL with the station ID if it wasn't already present
        constructed_url = f"https://tempestwx.com/map/{station_id}/{latitude}/{longitude}/{zoom}"
        print(f"Constructed URL: {constructed_url}")
        
        # Open the target webpage
        driver.get(constructed_url)
        time.sleep(5)  # Wait for page to fully load

        # Wait for the station-detail element to appear
        station_detail = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.ID, 'station-detail'))
        )

        # Extract the station ID from the href attribute
        station_info = station_detail.find_element(By.XPATH, './/a[contains(@href, "/station/")]')
        station_id = station_info.get_attribute('href').split('/station/')[1].split('?')[0]
        station_name = station_info.text.strip()
        station_identifier = f"{station_id} - {station_name}"

        # Look for 'sw-list'
        sw_list = station_detail.find_element(By.CLASS_NAME, 'sw-list')

        # Extract the data from sw-list
        data = {}
        wind_data = {}
        for item in sw_list.find_elements(By.CLASS_NAME, 'lv-value-display'):
            label = item.find_element(By.XPATH, '../span[@class="lv-param-label"]').text.strip().lower().replace(" ", "_")
            value = item.text.strip()

            if label == "timestamp" or label == "timezone":
                data[label] = {"value": value, "unit": None}
            else:
                numeric_value, unit = split_value_and_unit(value)

                if label == "rain_intensity":
                    unit = unit.replace(" ", "")

                data[label] = {"value": numeric_value, "unit": unit}

            if label == "wind_speed":
                wind_speed_mps = convert_wind_speed_to_mps(value.split()[0])
                wind_data["wind_speed"] = wind_speed_mps
            elif label == "wind_direction":
                wind_direction_degrees = convert_compass_to_degrees(value)
                if wind_direction_degrees is not None:
                    wind_data["wind_direction"] = wind_direction_degrees

        # Properly handle the timestamp value
        timestamp_value = data.get("timestamp", {}).get("value", "")
        timezone_value = data.get("timezone", {}).get("value", "")

        if timestamp_value and timezone_value:
            unix_time_ms = convert_timestamp_to_unix_ms(timestamp_value, timezone_value)
            if unix_time_ms is not None:
                data["timestamp_unix"] = {"value": unix_time_ms, "unit": "ms"}

        # Add descriptions to each key
        descriptions = {
            "air_density": "The mass of air per unit volume.",
            "air_temperature": "The temperature of the air.",
            "station_pressure": "The atmospheric pressure at the station.",
            "brightness": "The intensity of light.",
            "delta_t": "The difference between air temperature and dew point.",
            "dew_point": "The temperature at which air becomes saturated with moisture.",
            "feels_like": "The apparent temperature considering humidity and wind.",
            "heat_index": "The perceived temperature due to air temperature and humidity.",
            "lightning_strike_count": "The number of lightning strikes detected.",
            "lightning_detected_last_3_hrs": "The number of lightning strikes detected in the last 3 hours.",
            "lightning_distance_detected": "The estimated distance of detected lightning strikes.",
            "lightning_last_detected": "The time since the last lightning strike was detected.",
            "rain_intensity": "The rate of rainfall.",
            "rain_accumulation_(today)": "The total rainfall accumulated today.",
            "rain_accumulation_(yesterday)": "The total rainfall accumulated yesterday.",
            "rain_duration_(today)": "The duration of rainfall today.",
            "rain_duration_(yesterday)": "The duration of rainfall yesterday.",
            "relative_humidity": "The percentage of moisture in the air relative to saturation.",
            "sea_level_pressure": "The atmospheric pressure adjusted to sea level.",
            "solar_radiation": "The power per unit area received from the Sun.",
            "timestamp": "The date and time of the observation.",
            "timezone": "The timezone of the observation.",
            "timestamp_unix": "The timestamp in Unix time format.",
            "uv_index": "The ultraviolet index indicating the level of UV radiation.",
            "wet_bulb_temperature": "The lowest temperature air can reach by evaporative cooling.",
            "wind_speed": "The speed of the wind.",
            "wind_chill": "The perceived decrease in air temperature felt by the body.",
            "wind_direction": "The direction from which the wind is blowing.",
            "wind_gust": "The peak wind speed during a short time interval.",
            "wind_lull": "The minimum wind speed during a short time interval."
        }

        for key in data:
            if key in descriptions:
                data[key]["description"] = descriptions[key]

        # Convert data to JSON
        json_data = json.dumps(data)
        wind_speed_data = json.dumps({"wind_speed": wind_data.get("wind_speed")})
        wind_direction_data = json.dumps({"wind_direction": wind_data.get("wind_direction")})

        # Handle output to JSON file
        if json_file:
            with open(json_file, 'w') as f:
                f.write(json_data)
        
        # Handle output to plain ASCII file or stdout
        if output_file is not None:
            output_text = f"Station ID: {station_id}\nStation Name: {station_name}\n\n"
            for key, value in data.items():
                output_text += f"{key}: {value['value']} {value['unit'] if value['unit'] else ''}\n"
            with open(output_file, 'w') as f:
                f.write(output_text)

        # Handle MQTT output
        if mqtt_config:
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

                # Publish JSON data to MQTT server
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

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='This program extracts weather station data from any station displayed on the TempestWX map. It allows the user to output the data in JSON format, plain ASCII text, or publish it to an MQTT server. To obtain the URL for the map area of interest, go to https://tempestwx.com/map/50515/65.1557/-16.47/6. Then, navigate to the desired location on the map and zoom in until fewer than 50 stations are visible. Copy the URL from the browser\'s address bar and provide it to the script.',
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('url', type=str, nargs='?', help='The URL to process')
    parser.add_argument('-j', '--json', type=str, help='Output data to a JSON file')
    parser.add_argument('-o', '--output', nargs='?', const=None, help='Output data to a plain ASCII file. If not provided, print to stdout')
    parser.add_argument('-m', '--mqtt', type=str, nargs='?', const='tempestwx.json', help='MQTT configuration file')
    parser.add_argument('-w', '--windrose', type=str, nargs='?', const=True, help='Publish windrose MQTT data with optional topic name')
    parser.add_argument('-s', '--setup-mqtt', action='store_true', help='Setup MQTT configuration')
    args = parser.parse_args()

    if args.setup_mqtt:
        save_mqtt_config('tempestwx.json')
    elif not args.url and not args.mqtt:
        parser.print_help()
    else:
        main(args.url, json_file=args.json, output_file=args.output, mqtt_config=args.mqtt, windrose_topic=args.windrose)
