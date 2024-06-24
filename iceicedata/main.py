import json
import time
import os
import sys
import signal
import logging
import argparse
from iceicedata.data_processing import process_data, output_data
from iceicedata.mqtt_utils import send_mqtt_data
from iceicedata.config_handler import save_mqtt_config
from iceicedata.arg_parser import parse_arguments
from iceicedata.config_loader import load_config, validate_config

VERSION = "1.2.0"  # Important update increment


def signal_handler(sig, frame):
    print("\nProgram terminated by user.")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def main():
    parser = argparse.ArgumentParser(description='''

This program extracts weather station data from any station displayed on the TempestWX map.

Steps:
1. Obtain the URL for the map area of interest from https://tempestwx.com/map/.
2. Navigate to the desired location on the map and zoom in until fewer than 50 stations are visible.
3. Copy the URL from the browser's address bar and provide it to the script.

Options:
  -h, --help                    Show this help message and exit.
  -v, --version                 Show the version information and exit.
  -j FILE, --json FILE          Output data to a JSON file.
  -o FILE, --output FILE        Output data to a plain ASCII file. If not provided, print to stdout.
  -m [FILE], --mqtt [FILE]      Send data to the MQTT server using the configuration from FILE. Default: config.yaml.
  -w, --windrose                Publish windrose MQTT data. Uses 'mqtt_windrose_root' from the configuration file.
  -c FILE, --config FILE        Specify the configuration file to use. Default: config.yaml.
  -i ID, --station-id ID        The station ID to process.
  -r REPEAT, --repeat REPEAT    Repeat the data retrieval every N minutes or days. Specify as '5m' for minutes or '1d' for days (minimum 5 minutes or 1 day).
  -S, --setup-mqtt              Configure MQTT.

''', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-r', '--repeat', type=int, help=argparse.SUPPRESS)
    parser.add_argument('-i', '--station-id', type=str, help=argparse.SUPPRESS)
    parser.add_argument('-j', '--json', type=str, help=argparse.SUPPRESS)
    parser.add_argument('-o', '--output', type=str, nargs='?', const='', help=argparse.SUPPRESS)
    parser.add_argument('-m', '--mqtt', type=str, nargs='?', const='config.yaml', help=argparse.SUPPRESS)
    parser.add_argument('-w', '--windrose', action='store_true', help=argparse.SUPPRESS)
    parser.add_argument('-c', '--config', type=str, default='config.yaml', help=argparse.SUPPRESS)
    parser.add_argument('-v', '--version', action='store_true', help=argparse.SUPPRESS)
    parser.add_argument('-S', '--setup-mqtt', action='store_true', help=argparse.SUPPRESS)
    parser.add_argument('-d', '--debug', type=str, nargs='?', const='', help='Enable debug mode. Optionally specify a log file.')
    args = parser.parse_args()

    # Setup logging
    import logging
    log_level = logging.DEBUG if args.debug is not None else logging.INFO
    log_format = '%(asctime)s - %(levelname)s - %(message)s'
    if args.debug:
        log_file = args.debug if args.debug else None
        logging.basicConfig(level=log_level, format=log_format, filename=log_file, filemode='w')
    else:
        logging.basicConfig(level=log_level, format=log_format)
    logger = logging.getLogger()

    logger.debug("Starting main function with arguments: %s", args)
    # Load configuration
    config_file = args.config
    local_config_file = 'config.yaml'
    config = {}

    if os.path.isfile(local_config_file):
        logger.debug("Loading local configuration file: %s", local_config_file)
        config.update(load_config(local_config_file))

    if config_file and os.path.isfile(config_file):
        logger.debug("Loading specified configuration file: %s", config_file)
        config.update(load_config(config_file))

    if args.debug or config.get('debug', False):
        logger.setLevel(logging.DEBUG)
        logger.debug("Debug mode enabled from configuration file.")

    logger.debug("Configuration loaded: %s", config)
    if args.version:
        print("Version argument detected.")
        print(f"Version: {VERSION}")
        sys.exit(0)

    def validate_repeat(repeat):
        import re
        match = re.match(r'^(\d+)([md])$', repeat)
        if not match:
            print("Error: Invalid repeat format. Use '5m' for minutes or '1d' for days.")
            sys.exit(1)
        value, unit = match.groups()
        value = int(value)
        if unit == 'm' and value < 5:
            print("Error: The repeat delay must be at least 5 minutes.")
            sys.exit(1)
        if unit == 'd' and value < 1:
            print("Error: The repeat delay must be at least 1 day.")
            sys.exit(1)
        return value, unit

    if args.repeat:
        repeat_value, repeat_unit = validate_repeat(args.repeat)

    def validate_station_id(station_id):
        try:
            station_id = station_id.strip().lstrip('0')
            if not station_id.isdigit():
                raise ValueError
            station_id = int(station_id)
            if not (1 <= station_id <= 999999):
                raise ValueError
            return station_id
        except ValueError:
            print("Error: Invalid station ID. Please enter an integer between 1 and 999999.")
            sys.exit(1)

    if not args.station_id and not args.version:
        print("Error: The -i option is required unless -v is used.")
        sys.exit(1)

    if args.output is not None and args.output == '':
        print("Error: The -o option requires a filename.")
        sys.exit(1)

    if args.output:
        try:
            with open(args.output, 'w') as f:
                pass
        except IOError:
            print(f"Error: Cannot write to the output file '{args.output}'.")
            sys.exit(1)

    if args.config:
        try:
            config = load_config(args.config)
        except Exception as e:
            print(f"Error: Cannot load the configuration file '{args.config}': {e}")
            sys.exit(1)

    if args.mqtt is not None:
        if args.mqtt == '':
            args.mqtt = 'config.yaml'
        if not os.path.isfile(args.mqtt):
            print(f"Error: Configuration file '{args.mqtt}' not found. Please use the '-S' option to set up a new configuration or provide an existing configuration file with the '-m' option.")
            sys.exit(1)
        try:
            config = load_config(args.mqtt)
            required_keys = ["mqtt_server", "mqtt_port", "mqtt_root"]
            for key in required_keys:
                if key not in config:
                    print(f"Error: Missing required MQTT configuration parameter '{key}' in '{args.mqtt}'. Please use the '-S' option to generate a valid config.")
                    sys.exit(1)
            if not validate_config(config):
                print("Error: Invalid configuration format.")
                sys.exit(1)
        except Exception as e:
            print(f"Error: Cannot load the configuration file '{args.mqtt}': {e}")
            sys.exit(1)
    else:
        try:
            config_file = args.config
            config = load_config(config_file) or load_config('config.yaml')
            if not config:
                print("Error: Configuration file not found. Please use the '-S' option to set up a new configuration or provide an existing configuration file with the '-m' option.")
                sys.exit(1)
            if not validate_config(config):
                print("Error: Invalid configuration format.")
                sys.exit(1)
        except Exception as e:
            print(f"Error: Cannot load the configuration file '{config_file}': {e}")
            sys.exit(1)

        print("Validating station ID:", args.station_id)
        station_id = validate_station_id(args.station_id)
        print("Station ID validated:", station_id)
        final_url = f"https://tempestwx.com/map/{station_id}"  # Construct the URL using the station ID

        print(f"Looking for station {station_id} -", end='', flush=True)
        print("Processing data for URL:", final_url)
        try:
            data, wind_data, station_name, final_url = process_data(final_url)
        except Exception as e:
            print(f"Error: Failed to process the data from the URL: {e}")
            sys.exit(1)
        print("Data processing completed. Data:", data)
        if data is None or final_url is None:
            print("Data or final URL is None.")
            print("Failed to process the data from the URL.")
            return
        print(f" found. Station Name: {station_name}", end='')
        if args.repeat:
            print(f"; Retrieving data every {args.repeat} minutes.", end='')
        print()  # Move to the next line after the message

        if data is None or final_url is None:
            print("Failed to process the data from the URL.")
            return

        output_data(data, wind_data, json_file=args.json, output_file=args.output, stdout=True)

        station_identifier = f"{station_id} - {station_name}"

        if args.mqtt:
            print("Sending data to MQTT server.")
            config = load_config(args.mqtt)
            send_mqtt_data(data, config, f"{config['mqtt_root']}{station_identifier}")

        if args.windrose:
            print("Publishing windrose data to MQTT server.")
            config = load_config('config.yaml')
            if not config.get('mqtt_windrose_root'):
                print("Windrose root topic is not set in the configuration file. Please add it to the configuration file and try again.")
            else:
                windrose_data = {"wind_speed": wind_data.get("wind_speed"), "wind_direction": wind_data.get("wind_direction")}
                send_mqtt_data(windrose_data, config, f"{config['mqtt_windrose_root']}{station_identifier}")

        # Repeat the data retrieval and processing if the repeat parameter is provided
        while args.repeat is not None:
            time.sleep(args.repeat * 60)

            try:
                data, wind_data, station_name, final_url = process_data(final_url, skip_initial=True)
            except Exception as e:
                print(f"Error: Failed to process the data from the URL: {e}")
                sys.exit(1)

            if data is None or final_url is None:
                print("Failed to process the data from the URL.")
                return

            station_identifier = f"{station_id} - {station_name}"

            output_data(data, wind_data, json_file=args.json, output_file=args.output, stdout=True)

            if args.mqtt:
                config = load_config(args.mqtt)
                send_mqtt_data(data, config, f"{config['mqtt_root']}{station_identifier}")

            if args.windrose:
                config = load_config('config.yaml')
                if not config.get('mqtt_windrose_root'):
                    print("Windrose root topic is not set in the configuration file. Please add it to the configuration file and try again.")
                else:
                    windrose_data = {"wind_speed": wind_data.get("wind_speed"), "wind_direction": wind_data.get("wind_direction")}
                    send_mqtt_data(windrose_data, config, f"{config['mqtt_windrose_root']}{station_identifier}")

        if args.json or args.output:
            output_data(data, wind_data, json_file=args.json, output_file=args.output, stdout=False)

        if args.mqtt:
            config = load_config(args.mqtt)
            send_mqtt_data(data, config, f"{config['mqtt_root']}{station_identifier}")

        if args.windrose:
            config = load_config('config.yaml')
            if not config.get('mqtt_windrose_root'):
                print("Windrose root topic is not set in the configuration file. Please add it to the configuration file and try again.")
            else:
                windrose_data = {"wind_speed": wind_data.get("wind_speed"), "wind_direction": wind_data.get("wind_direction")}
                send_mqtt_data(windrose_data, config, f"{config['mqtt_windrose_root']}{station_identifier}")

        # Repeat the data retrieval and processing if the repeat parameter is provided
        while args.repeat is not None:
            print(f"Waiting for {args.repeat} minutes before repeating...")
            time.sleep(args.repeat * 60)

            data, wind_data, station_name, final_url = process_data(final_url, skip_initial=True)

            if data is None:
                print("Failed to process the data from the URL.")
                return

            station_identifier = f"{station_id} - {station_name}"

            output_data(data, wind_data, json_file=args.json, output_file=args.output, stdout=True)

            if args.mqtt:
                config = load_config(args.mqtt)
                send_mqtt_data(data, config, f"{config['mqtt_root']}{station_identifier}")

            if args.windrose:
                config = load_config('config.yaml')
                if not config.get('mqtt_windrose_root'):
                    print("Windrose root topic is not set in the configuration file. Please add it to the configuration file and try again.")
                else:
                    windrose_data = {"wind_speed": wind_data.get("wind_speed"), "wind_direction": wind_data.get("wind_direction")}
                    send_mqtt_data(windrose_data, config, f"{config['mqtt_windrose_root']}{station_identifier}")

if __name__ == "__main__":
    main()
