import argparse

def parse_arguments(config):
    parser = argparse.ArgumentParser(description='''

This program extracts weather station data from any station displayed on the TempestWX map.

Steps:
1. Edit the config.yaml file to include any required parameters.
2. Obtain the station ID for the map area of interest from https://tempestwx.com/map/:
  a. Click on the station of interest
  b. Note the station ID in the URL, e.g. "https://tempestwx.com/map/41866/63.4814/-20.2043/5" has a station ID of 41866
  c. Include the station ID using the '-i' option
  d. Multiple stations can be comma-separated or included in an optionally specified file.
3. Select the output option(s) required (JSON, ASCII, MQTT, database)
4. Include a repeat option if you want it to continuously obtain data, via the -r option.


Options:
  -h, --help                    Show this help message and exit.
  -v, --version                 Show the version information and exit.
  -j FILE, --json FILE          Output data to a JSON file.
  -o FILE, --output FILE        Output data to a plain ASCII file. If not provided, print to stdout.
  -m [FILE], --mqtt [FILE]      Send data to the MQTT server using the configuration from FILE. Default: config.yaml.
  -w, --windrose                Publish windrose MQTT data. Uses 'mqtt_windrose_root' from the configuration file.
  -c FILE, --config FILE        Specify the configuration file to use. Default: config.yaml.
  -i ID, --station-id ID        Comma-separated list of station IDs or a file containing station IDs to process.
  -r REPEAT, --repeat REPEAT    Repeat the data retrieval every N minutes or days. Specify as '5m' for minutes or '1d' for days (minimum 5 minutes or 1 day).
  -S, --setup-mqtt              Configure MQTT.
  --database [DATABASE]         Path and name of the database file (default: value from config.yaml or 'weather_data.db')
  -d [DEBUG], --debug [DEBUG]   Enable debug mode. Optionally specify a log file.
  -R TYPE, --report TYPE        Generate a report. Types: daily, weekly, monthly.
  --start-date START_DATE       Start date for the report (YYYY-MM-DD).
  --end-date END_DATE           End date for the report (YYYY-MM-DD).
  --output-format FORMAT        Report output format: pdf, html, csv (default: pdf).


''', formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('-r', '--repeat', type=str, help=argparse.SUPPRESS)
    parser.add_argument('-i', '--station-id', type=str, help='Comma-separated list of station IDs or a file containing station IDs.')
    parser.add_argument('-j', '--json', type=str, help=argparse.SUPPRESS)
    parser.add_argument('-o', '--output', type=str, nargs='?', const='', help=argparse.SUPPRESS)
    parser.add_argument('-m', '--mqtt', type=str, nargs='?', const='config.yaml', help=argparse.SUPPRESS)
    parser.add_argument('-w', '--windrose', action='store_true', help=argparse.SUPPRESS)
    parser.add_argument('-c', '--config', type=str, default='config.yaml', help=argparse.SUPPRESS)
    parser.add_argument('-v', '--version', action='store_true', help=argparse.SUPPRESS)
    parser.add_argument('-S', '--setup-mqtt', action='store_true', help=argparse.SUPPRESS)
    parser.add_argument('--database', type=str, nargs='?', const=config.get('database_file', 'weather_data.db'), help='Path and name of the database file (default: value from config.yaml or "weather_data.db")')
    parser.add_argument('-d', '--debug', type=str, nargs='?', const='', help='Enable debug mode. Optionally specify a log file.')
    parser.add_argument('-R', '--report', type=str, choices=['daily', 'weekly', 'monthly'], help='Generate a report.')
    parser.add_argument('--start-date', type=str, help='Start date for the report (YYYY-MM-DD).')
    parser.add_argument('--end-date', type=str, help='End date for the report (YYYY-MM-DD).')
    parser.add_argument('--output-format', type=str, choices=['pdf', 'html', 'csv'], default='pdf', help='Report output format.')
    
    return parser.parse_args()