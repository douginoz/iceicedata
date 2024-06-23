import argparse
from iceicedata.config import save_mqtt_config
from iceicedata.selenium_utils import initialize_driver, validate_url, extract_coordinates, get_station_id_from_url, get_placemarkers, select_placemarker, get_station_id
from iceicedata.data_processing import process_station_data
from iceicedata.mqtt_utils import publish_to_mqtt

def main(url=None, json_file=None, output_file=None, mqtt_config=None, windrose_topic=None):
    driver = None
    try:
        if not url:
            return
        driver = initialize_driver()
        final_url = validate_url(url)
        latitude, longitude, zoom = extract_coordinates(final_url)
        station_id = get_station_id_from_url(final_url)
        
        if not station_id:
            placemarker_titles, placemarkers = get_placemarkers(driver, final_url)
            if not placemarkers:
                return
            selection = select_placemarker(placemarker_titles)
            if selection == -1:
                return
            station_id = get_station_id(driver, placemarkers[selection])
            if not station_id:
                print("Failed to retrieve the station ID.")
                return
        
        constructed_url = f"https://tempestwx.com/map/{station_id}/{latitude}/{longitude}/{zoom}"
        data, wind_data, station_identifier = process_station_data(driver, constructed_url)
        
        # Handle output to JSON file
        if json_file:
            with open(json_file, 'w') as f:
                f.write(data)
        
        # Handle output to plain ASCII file or stdout
        if output_file is not None:
            with open(output_file, 'w') as f:
                f.write(data)

        # Handle MQTT output
        if mqtt_config:
            publish_to_mqtt(mqtt_config, data, wind_data, station_identifier, windrose_topic)

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='This program extracts weather station data from any station displayed on the TempestWX map.')
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
