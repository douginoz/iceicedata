# main.py
import json
import time
import os
import sys
import signal
import logging
import argparse
from datetime import datetime, timedelta
from data_processing import process_data, output_data
from mqtt_utils import send_mqtt_data
from config_handler import save_config, save_mqtt_config
from arg_parser import parse_arguments
from config_loader import load_config, validate_config
from database import create_database, insert_data_into_database, check_database_integrity, get_data_range
from report_generator import generate_report

VERSION = "1.4.0"

def signal_handler(sig, frame):
    print("\nProgram terminated by user.")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

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

def main():
    config_file = 'config.yaml'
    local_config_file = 'config.yaml'
    config = {}

    if os.path.isfile(local_config_file):
        config.update(load_config(local_config_file))

    args = parse_arguments(config)

    # Setup logging
    log_level = logging.INFO if args.debug is None else logging.DEBUG
    log_format = '%(asctime)s - %(levelname)s - %(message)s'
    log_file = args.debug if args.debug and args.debug != '' else None
    logging.basicConfig(level=log_level, format=log_format, filename=log_file, filemode='w')
    logger = logging.getLogger()

    logger.debug("Starting main function with arguments: %s", args)

    if args.version:
        print(f"Version: {VERSION}")
        sys.exit(0)

    if args.repeat:
        repeat_value, repeat_unit = validate_repeat(args.repeat)

    if args.setup_mqtt:
        logger.debug("Setting up MQTT configuration.")
        save_mqtt_config(config_file)
        sys.exit(0)

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

    if args.mqtt is not None or args.windrose:
        if not config:
            print(f"Error: Configuration file '{config_file}' not found or invalid. Please use the '-S' option to set up a new configuration or provide an existing configuration file with the '-m' option.")
            sys.exit(1)

        required_keys = ["mqtt_server", "mqtt_port", "mqtt_root"]
        for key in required_keys:
            if key not in config:
                print(f"Error: Missing required MQTT configuration parameter '{key}' in '{config_file}'. Please use the '-S' option to generate a valid config.")
                sys.exit(1)

        if not validate_config(config):
            print("Error: Invalid configuration format.")
            sys.exit(1)

    station_ids = []
    if args.station_id:
        if os.path.isfile(args.station_id):
            with open(args.station_id, 'r') as f:
                station_ids = [validate_station_id(line.strip()) for line in f if line.strip().isdigit()]
        else:
            logger.debug("Validating multiple station IDs: %s", args.station_id)
            station_ids = [validate_station_id(station_id.strip()) for station_id in args.station_id.split(',')]

    # Create the database if specified
    if args.database is not None:
        database_file = args.database
        create_database(database_file)
        check_database_integrity(database_file)

    # Handle report generation
    if args.report:
        logger.info("Generating report...")
        
        # Get the range of available data
        data_start, data_end = get_data_range(config['database_file'])
        
        if data_start is None or data_end is None:
            logger.error("No data available in the database or unable to parse date range.")
            sys.exit(1)
        
        # Parse the start_date or use the earliest available data
        start_date = datetime.strptime(args.start_date, "%Y-%m-%d").date() if args.start_date else data_start.date()
        
        # Parse the end_date or use today's date
        end_date = datetime.strptime(args.end_date, "%Y-%m-%d").date() if args.end_date else datetime.now().date()
        
        # Adjust dates if they're outside the available range
        start_date = max(start_date, data_start.date())
        end_date = min(end_date, data_end.date())
        
        if start_date > end_date:
            logger.error("Start date is after end date or no data available in the specified range.")
            sys.exit(1)
        
        generate_report(args.report, start_date, end_date, args.output_format, config)
        sys.exit(0)

    while True:  # Main processing loop for repeated execution
        for station_id in station_ids:
            logger.debug("Processing data for Station ID: %s", station_id)
            final_url = f"https://tempestwx.com/map/{station_id}"
            
            print(f"Looking for station {station_id} -", end='', flush=True)
            logger.debug("Processing data for URL: %s", final_url)
            try:
                data, wind_data, station_name, attribute_descriptions = process_data(final_url)
            except Exception as e:
                print(f"Error: Failed to process the data from the URL: {e}")
                continue

            logger.debug("Data processing completed. Data: %s", data)
            logger.debug("Attribute descriptions: %s", attribute_descriptions)
            if data is None:
                print("Data is None.")
                print(f"Failed to process the data for station ID {station_id}.")
                continue

            print(f" found. Station Name: {station_name}", end='')
            print()

            output_data(data, wind_data, json_file=args.json, output_file=args.output, stdout=True)

            station_identifier = f"{station_id} - {station_name}"

            if args.mqtt or args.windrose:
                if args.mqtt:
                    send_mqtt_data(data, config, f"{config['mqtt_root']}{station_identifier}")

                if args.windrose:
                    if not config.get('mqtt_windrose_root'):
                        print("Windrose root topic is not set in the configuration file. Please add it to the configuration file and try again.")
                    else:
                        windrose_data = {
                            "wind_speed": data['wind_speed']['value'],
                            "wind_direction": data['wind_direction']['value']
                        }
                        send_mqtt_data(windrose_data, config, f"{config['mqtt_windrose_root']}{station_identifier}")

            if args.database is not None:
                logger.debug("Inserting data into database. Attribute descriptions: %s", attribute_descriptions)
                insert_data_into_database(database_file, data, attribute_descriptions)

            if args.json or args.output:
                output_data(data, wind_data, json_file=args.json, output_file=args.output, stdout=False)

        if args.repeat:
            logger.debug("Waiting for next iteration...")
            if repeat_unit == 'm':
                time.sleep(repeat_value * 60)
            elif repeat_unit == 'd':
                time.sleep(repeat_value * 86400)
        else:
            break

if __name__ == "__main__":
    main()