# data_processing.py
import logging
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.common.exceptions import NoSuchElementException
from helper import convert_wind_speed_to_mps, split_value_and_unit, convert_timestamp_to_unix_ms, convert_compass_to_degrees

def process_data(url, skip_initial=False):
    logger = logging.getLogger()
    logger.debug("Starting data processing for URL: %s", url)
    driver = None

    try:
        # Initialize the WebDriver
        service = Service('/usr/local/bin/geckodriver')
        options = webdriver.FirefoxOptions()
        options.add_argument('--headless')
        driver = webdriver.Firefox(service=service, options=options)

        driver.get(url)
        logger.debug("Navigated to URL: %s", url)
        time.sleep(10)  # Wait for the page to fully load

        try:
            station_detail = WebDriverWait(driver, 40).until(
                EC.visibility_of_element_located((By.ID, 'station-detail'))
            )

            # Extract the station ID from the href attribute
            station_info = station_detail.find_element(By.XPATH, './/a[contains(@href, "/station/")]')
            station_id = station_info.get_attribute('href').split('/station/')[1].split('?')[0]
            station_name = station_info.text.strip()
            station_identifier = f"{station_id} - {station_name}"

            # Initialize the data dictionary with all expected keys
            data = {
                'station_id': station_id,
                'station_name': station_name,
                'air_density': {'value': None, 'unit': None, 'description': "The mass of air per unit volume."},
                'air_temperature': {'value': None, 'unit': None, 'description': "The temperature of the air."},
                'station_pressure': {'value': None, 'unit': None, 'description': "The atmospheric pressure at the station."},
                'brightness': {'value': None, 'unit': None, 'description': "The intensity of light."},
                'delta_t': {'value': None, 'unit': None, 'description': "The difference between air temperature and dew point."},
                'dew_point': {'value': None, 'unit': None, 'description': "The temperature at which air becomes saturated with moisture."},
                'feels_like': {'value': None, 'unit': None, 'description': "The apparent temperature considering humidity and wind."},
                'heat_index': {'value': None, 'unit': None, 'description': "The perceived temperature due to air temperature and humidity."},
                'lightning_strike_count': {'value': None, 'unit': None, 'description': "The number of lightning strikes detected."},
                'lightning_detected_last_3_hrs': {'value': None, 'unit': None, 'description': "The number of lightning strikes detected in the last 3 hours."},
                'lightning_distance_detected': {'value': None, 'unit': None, 'description': "The estimated distance of detected lightning strikes."},
                'lightning_last_detected': {'value': None, 'unit': None, 'description': "The time since the last lightning strike was detected."},
                'rain_intensity': {'value': None, 'unit': None, 'description': "The rate of rainfall."},
                'rain_accumulation_today': {'value': None, 'unit': None, 'description': "The total rainfall accumulated today."},
                'rain_accumulation_yesterday': {'value': None, 'unit': None, 'description': "The total rainfall accumulated yesterday."},
                'rain_duration_today': {'value': None, 'unit': None, 'description': "The duration of rainfall today."},
                'rain_duration_yesterday': {'value': None, 'unit': None, 'description': "The duration of rainfall yesterday."},
                'relative_humidity': {'value': None, 'unit': None, 'description': "The percentage of moisture in the air relative to saturation."},
                'sea_level_pressure': {'value': None, 'unit': None, 'description': "The atmospheric pressure adjusted to sea level."},
                'solar_radiation': {'value': None, 'unit': None, 'description': "The power per unit area received from the Sun."},
                'timestamp': {'value': None, 'unit': None, 'description': "The date and time of the observation."},
                'timezone': {'value': None, 'unit': None, 'description': "The timezone of the observation."},
                'timestamp_unix': {'value': None, 'unit': None, 'description': "The timestamp in Unix time format."},
                'uv_index': {'value': None, 'unit': None, 'description': "The ultraviolet index indicating the level of UV radiation."},
                'wet_bulb_temperature': {'value': None, 'unit': None, 'description': "The lowest temperature air can reach by evaporative cooling."},
                'wind_speed': {'value': None, 'unit': None, 'description': "The speed of the wind."},
                'wind_chill': {'value': None, 'unit': None, 'description': "The perceived decrease in air temperature felt by the body."},
                'wind_direction': {'value': None, 'unit': None, 'description': "The direction from which the wind is blowing."},
                'wind_gust': {'value': None, 'unit': None, 'description': "The peak wind speed during a short time interval."},
                'wind_lull': {'value': None, 'unit': None, 'description': "The minimum wind speed during a short time interval."}
            }

            # Initialize the wind_data dictionary
            wind_data = {
                'wind_speed': None,
                'wind_direction': None
            }

            # Populate the data dictionary with values from the website
            sw_list = station_detail.find_element(By.CLASS_NAME, 'sw-list')
            for item in sw_list.find_elements(By.CLASS_NAME, 'lv-value-display'):
                label = item.find_element(By.XPATH, '../span[@class="lv-param-label"]').text.strip().lower().replace(" ", "_")
                value = item.text.strip()

                if label in data:
                    numeric_value, unit = split_value_and_unit(value)
                    data[label]['value'] = numeric_value
                    data[label]['unit'] = unit

            # Handling timestamp and timezone
            if 'timestamp' in data and data['timestamp']['value'] is not None:
                timezone_value = data['timezone']['value'] if 'timezone' in data else None
                unix_time_ms = convert_timestamp_to_unix_ms(data['timestamp']['value'], timezone_value)
                if unix_time_ms is not None:
                    data['timestamp_unix']['value'] = unix_time_ms
            else:
                logger.warning("Timestamp or timezone is missing in the data.")

        except NoSuchElementException:
            logger.error("Station details not found.")
            print(f"Error: Station ID {station_id} not found on the website.")
            return None, None, None, None

        logger.debug("Data extraction completed. Data: %s", data)
        
        # Prepare attribute descriptions to be passed to insert function
        attribute_descriptions = {
            key: value['description'] for key, value in data.items() if 'description' in value
        }

        # Log the attribute descriptions
        logger.debug("Attribute descriptions prepared: %s", attribute_descriptions)

        return data, wind_data, station_name, attribute_descriptions
    except Exception as e:
        logger.error("An error occurred: %s", e)
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
    
    if stdout and not output_file:
        print(json_data)

    if json_file:
        if not json_file.endswith('.json'):
            json_file += '.json'
        with open(json_file, 'w') as f:
            f.write(json_data)

    if output_file and output_file != '/dev/null':
        with open(output_file, 'w') as f:
            for key, value in data.items():
                value_str = f'"{value["value"]}"' if "value" in value else '""'
                unit_str = f'"{value["unit"]}"' if "unit" in value else '""'
                description_str = f'"{value["description"]}"' if "description" in value else '""'
                f.write(f'"{key}",{value_str},{unit_str},{description_str}\n')