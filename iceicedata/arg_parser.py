import argparse

def parse_arguments():
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
    parser.add_argument('-m', '--mqtt', type=str, nargs='?', const='iceicedata.json', help=argparse.SUPPRESS)
    parser.add_argument('-w', '--windrose', action='store_true', help=argparse.SUPPRESS)
    parser.add_argument('-c', '--config', type=str, default='config.yaml', help=argparse.SUPPRESS)
    parser.add_argument('-v', '--version', action='store_true', help=argparse.SUPPRESS)
    parser.add_argument('-S', '--setup-mqtt', action='store_true', help=argparse.SUPPRESS)
    parser.add_argument('-d', '--debug', type=str, nargs='?', const='', help='Enable debug mode. Optionally specify a log file.')
    return parser.parse_args()