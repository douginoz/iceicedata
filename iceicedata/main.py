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
from iceicedata.data_processing import process_data, output_data
from iceicedata.mqtt_utils import send_mqtt_data, load_config, save_mqtt_config
from iceicedata.helper import validate_url  # Correct import

VERSION = "1.1.4"  # Incremented version

class CustomHelpFormatter(argparse.RawTextHelpFormatter):
    def add_arguments(self, actions):
        for action in actions:
            if action.help == argparse.SUPPRESS:
                continue
            self._add_item(self._format_action, [action])
    
    def add_argument_group(self, group):
        if group.title == 'optional arguments':
            return
        super().add_argument_group(group)

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

  -o FILE, --output FILE        Output data to a plain ASCII file. If not provided,
                                print to stdout.

  -s, --stdout                  Display data on stdout.

  -m [FILE], --mqtt [FILE]      Send data to the MQTT server using the configuration
                                from FILE. Default: iceicedata.json.

  -w, --windrose                Publish windrose MQTT data. Uses 'mqtt_windrose_root'
                                from the configuration file.

  -S, --setup-mqtt              Setup MQTT configuration and save to a file. This
                                option is mutually exclusive with -m.
  -u URL, --url URL             The URL to process.
  ''', formatter_class=CustomHelpFormatter)
    parser.add_argument('-u', '--url', type=str, help=argparse.SUPPRESS)
    parser.add_argument('-j', '--json', type=str, help=argparse.SUPPRESS)
    parser.add_argument('-o', '--output', type=str, help=argparse.SUPPRESS)
    parser.add_argument('-s', '--stdout', action='store_true', help=argparse.SUPPRESS)
    parser.add_argument('-m', '--mqtt', type=str, nargs='?', const='iceicedata.json', help=argparse.SUPPRESS)
    parser.add_argument('-w', '--windrose', action='store_true', help=argparse.SUPPRESS)
    parser.add_argument('-S', '--setup-mqtt', action='store_true', help=argparse.SUPPRESS)
    parser.add_argument('-v', '--version', action='store_true', help=argparse.SUPPRESS)
    args = parser.parse_args()

    if args.version:
        print(f"Version: {VERSION}")
    elif args.setup_mqtt:
        if args.mqtt:
            print("Error: --setup-mqtt (-S) and --mqtt (-m) options cannot be used together.")
            sys.exit(1)
        save_mqtt_config('iceicedata.json')
    elif not args.url and not args.mqtt:
        parser.print_help()
    elif not args.url:
        print("Error: URL must be provided. Use the -u or --url option to specify the URL.")
        sys.exit(1)
    else:
        data, wind_data, station_identifier = process_data(args.url)

        if data is None:
            print("Failed to process the data from the URL.")
            return

        if args.stdout or args.json or args.output:
            output_data(data, wind_data, json_file=args.json, output_file=args.output, stdout=args.stdout)

        if args.mqtt:
            config = load_config(args.mqtt)
            send_mqtt_data(data, config, f"{config['mqtt_root']}{station_identifier}")

        if args.windrose:
            config = load_config('iceicedata.json')
            if not config.get('mqtt_windrose_root'):
                print("Windrose root topic is not set in the configuration file. Please add it to the configuration file and try again.")
            else:
                windrose_data = {"wind_speed": wind_data.get("wind_speed"), "wind_direction": wind_data.get("wind_direction")}
                send_mqtt_data(windrose_data, config, f"{config['mqtt_windrose_root']}{station_identifier}")

if __name__ == "__main__":
    main()
