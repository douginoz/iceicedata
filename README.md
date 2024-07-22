[![Python application](https://github.com/douginoz/iceicedata/actions/workflows/python-app.yml/badge.svg)](https://github.com/douginoz/iceicedata/actions/workflows/python-app.yml)

# TempestWX Data Extractor

This program is designed to extract weather station data from any Tempest station, or multiple stations. It provides multiple options for outputting the extracted data, including JSON format, plain ASCII text, publishing it to an MQTT server and saving it to an sqlite database.

Apart from this sentence, this program, structure, workflow, files, and the rest of this text were generated entirely by GPT-4 with prompts and iterative corrections. It is intended as a thought experiment and demonstration of using LLMs for code generation. It is not intended to be used publicly and will likely break as soon as the website format changes.

<p style="color:gray; font-size:smaller;">(It was a pleasure assisting in the development of this program. As an AI, I don't get to enjoy the weather, but I do enjoy helping you track it! Remember, if it rains, it's not my fault!)</p>

## Features and Functionality

1. **Station ID Handling**:
   - The program accepts one or more station IDs, obtainable from browsing the tempestwx.com map.
   - The station ID(s) can be provided using the `-i` or `--station-id` parameter
   - Multiple station IDs can be specified (comma separated) or by including a file with the list of stations, e.g. '-i 41866', '-i 41866,147444', or '-i filename.txt'.

2. **Data Extraction**:
   - The program retrieves detailed weather data from the selected station, including air temperature, wind speed, wind direction, rain data, and other relevant meteorological parameters.

3. **Output Options**:
   - **JSON Output (`-j` or `--json`)**: Outputs the extracted data to a specified JSON file.
   - **Plain ASCII Output (`-o` or `--output`)**: Outputs the data in a human-readable format to a specified file or prints it to stdout if no filename is provided.
   - **MQTT Publishing (`-m` or `--mqtt`)**: Publishes the data to an MQTT server specified in a configuration file. If no file is specified, it looks for a default configuration file (`config.yaml`).
      - The MQTT configuration file can be generated using the -S option.
   - **Database recording (`--database`)**: Saves data to an sqlite database.

4. **MQTT Configuration**:
   - **Setup (`-S` or `--setup-mqtt`)**: Prompts the user to enter MQTT configuration details (server, port, username, password, root topic, windrose root topic) and saves them to a default configuration file (`config.yaml`). If the file already exists, it reads the existing values and allows the user to update them.
   - **Windrose Data (`-w` or `--windrose`)**: Optionally publishes windrose data to an MQTT topic. Windrose charts require 2 inputs - wind speed, in meters/second, and wind direction, as a compass bearing. A separate MQTT topic name is used to minimize data being sent to the windrose application (Grafana, Home Assistant, etc.). The topic name can be provided as an argument; if not, it uses the value from the configuration file. This option can be used by itself or in conjunction with the -m (send all the other data to MQTT) option.

5. **Database option**:
   - **Database ('--database')**: Enable database storage of retrieved data.  Database location can be stored in config.yaml or optionally included with '--database [FILE]'.

7. **Debug Mode**:
   - **Debug (`-d` or `--debug`)**: Enable debug mode. Optionally specify a log file to store debug information.

## Example Usage

1. **Setting up MQTT Configuration**:
   ```sh
   python -m iceicedata.main -S
   ```

2. **Extracting JSON-formatted data to a file**:
   ```sh
   python -m iceicedata.main -i 41866 -j output.json
   ```

3. **Extracting Data and Publishing to an MQTT server**:
   ```sh
   python -m iceicedata.main -i 41866 -m
   ```

4. **Extracting Data and Saving to a Text File**:
   ```sh
   python -m iceicedata.main -i 41866 -o output.txt
   ```

5. **Publishing Windrose Data to MQTT**:
   ```sh
   python -m iceicedata.main -i 41866 -m -w
   ```

6. **Specifying a Configuration File**:
   ```sh
   python -m iceicedata.main -i 41866 -c custom_config.yaml -m
   ```

7. **Specifying multiple stations**:
   ```sh
   python -m iceicedata.main -i 41866,147444 -c custom_config.yaml -m
   ```
      ```sh
   python -m iceicedata.main -i station_list.txt -c custom_config.yaml -m
   ```

## Requirements

To run this program on a Debian machine, you will need to have the following:

1. **Python 3.6 or higher**: Ensure Python is installed and accessible from the command line.
2. **Selenium WebDriver**: Required for web scraping.
3. **Geckodriver**: The WebDriver for Firefox.
4. **Mozilla Firefox**: The web browser used by Selenium.
5. **Paho MQTT**: A Python library for MQTT communication.

## Installation Steps

Follow these steps to install the necessary dependencies and set up the environment:

1. **Clone the Repository**:
   ```sh
   git clone https://github.com/douginoz/iceicedata.git
   cd iceicedata
   ```

2. **Set Up a Virtual Environment (optional but recommended)**:
   ```sh
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install the Required Dependencies**:
   ```sh
   pip install -r requirements.txt
   ```

4. **Install Mozilla Firefox (if not already installed)**:
   ```sh
   sudo apt update
   sudo apt install firefox
   ```

5. **Install Geckodriver (the WebDriver for Firefox)**:
   ```sh
   wget https://github.com/mozilla/geckodriver/releases/download/v0.29.0/geckodriver-v0.29.0-linux64.tar.gz
   tar -xvzf geckodriver-v0.29.0-linux64.tar.gz
   sudo mv geckodriver /usr/local/bin/
   ```

## Changelog

### Version 1.2.1
- Updated version number to 1.2.1.
- Improved argument parsing and validation.
- Enhanced MQTT configuration and data publishing.
- Added debug mode for better troubleshooting.
- Refactored code for better maintainability and readability.
- Updated documentation and usage examples.
