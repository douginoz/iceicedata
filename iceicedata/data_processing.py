import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import sys
from datetime import datetime
import pytz
from iceicedata.helper import convert_wind_speed_to_mps, split_value_and_unit, convert_timestamp_to_unix_ms, convert_compass_to_degrees, validate_url, extract_coordinates, get_station_id_from_url
from iceicedata.selenium_utils import get_station_id

def process_data(url, skip_initial=False):
    driver = None

    try:
        # Initialize the WebDriver
        service = Service('/usr/local/bin/geckodriver')
        options = webdriver.FirefoxOptions()
        options.add_argument('--headless')
        driver = webdriver.Firefox(service=service, options=options)
        
        
        print(f"Opening URL: {url}")
        driver.get(url)
        time.sleep(10)  # Wait for page to fully load
        print("Page loaded.")

        # Wait for the station-detail element to appear
        print("Waiting for station-detail element to appear...")
        print("Waiting for station-detail element to appear...")
        station_detail = WebDriverWait(driver, 40).until(
            EC.visibility_of_element_located((By.ID, 'station-detail'))
        )

        # Extract the station ID from the href attribute
        print("station-detail element found.")
        print("station-detail element found.")
        station_info = station_detail.find_element(By.XPATH, './/a[contains(@href, "/station/")]')
        print("Station info element found.")
        print("Station info element found.")
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

        return data, wind_data, station_identifier, url if not skip_initial else url

    except Exception as e:
        print(f"An error occurred: {e}")
        return None, None, None, None

    finally:
        if driver:
            driver.quit()

def output_data(data, wind_data, json_file=None, output_file=None, stdout=False):
    if data is None:
        print("No data to output.")
        return

    json_data = json.dumps(data)
    wind_speed_data = json.dumps({"wind_speed": wind_data.get("wind_speed")})
    wind_direction_data = json.dumps({"wind_direction": wind_data.get("wind_direction")})

    if stdout:
        print(json_data)

    if json_file:
        with open(json_file, 'w') as f:
            f.write(json_data)

    if output_file:
        output_text = json.dumps(data, indent=2)
        with open(output_file, 'w') as f:
            f.write(output_text)
