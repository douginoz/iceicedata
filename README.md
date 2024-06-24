[![Python application](https://github.com/douginoz/iceicedata/actions/workflows/python-app.yml/badge.svg)](https://github.com/douginoz/iceicedata/actions/workflows/python-app.yml)

# TempestWX Data Extractor

This program is designed to extract weather station data from any station displayed on the TempestWX map. It provides multiple options for outputting the extracted data, including JSON format, plain ASCII text, or publishing it to an MQTT server.

Apart from this paragraph, this program, structure, workflow, files, and the rest of this text were generated entirely by GPT-4 with prompts and iterative corrections. It is intended as a thought experiment and demonstration of using LLMs for code generation. It is not intended to be used publicly and will likely break as soon as the website format changes.

## Features and Functionality

1. **URL Handling**:
   - The program accepts a URL pointing to an area on a TempestWX map that shows Tempest station installations.
   - If the map URL contains more than one station, the program scans for and lists all available placemarkers (weather stations) on the map, up to 50, allowing the user to select one.
   - If more than 50 placemarkers are found, the program prompts the user to zoom in closer to reduce the number of visible placemarkers.
   - Any location on Earth can be selected.

2. **Data Extraction**:
   - The program retrieves detailed weather data from the selected station, including air temperature, wind speed, wind direction, rain data, and other relevant meteorological parameters.

3. **Output Options**:
   - **JSON Output (`-j` or `--json`)**: Outputs the extracted data to a specified JSON file.
   - **Plain ASCII Output (`-o` or `--output`)**: Outputs the data in a human-readable format to a specified file or prints it to stdout if no filename is provided.
   - **MQTT Publishing (`-m` or `--mqtt`)**: Publishes the data to an MQTT server specified in a configuration file. If no file is specified, it looks for a default configuration file (`iceicedata.json`).
      - The MQTT configuration file can be generated using the -S option.

4. **MQTT Configuration**:
   - **Setup (`-S` or `--setup-mqtt`)**: Prompts the user to enter MQTT configuration details (server, port, username, password, root topic, windrose root topic) and saves them to a default configuration file (`iceicedata.json`). If the file already exists, it reads the existing values and allows the user to update them.
   - **Windrose Data (`-w` or `--windrose`)**: Optionally publishes windrose data to an MQTT topic. Winrose charts require 2 inputs - wind speed, in meters/second, and wind direction, as a compass bearing.  A separate MQSS topic name is used to minimize data being sent to the winrose application (grafana, Home Assistant etc). The topic name can be provided as an argument; if not, it uses the value from the configuration file.  This option can be used by itself or in conjunction with the -m (send all the other data to MQTT) option.

## Example Usage

1. **Setrting up MQTT Configuration**:
   ```sh
   python -m iceicedata.main -S

2. **Extracting JSON-formmated data to a file**:
   ```sh
   python -m iceicedata.main -u "https://tempestwx.com/map/50515/65.1557/-16.47/6" -j output.json

3. **Extracting Data and Publishing to a MQTT server**:
   ```sh
   python -m iceicedata.main -u "https://tempestwx.com/map/50515/65.1557/-16.47/6" -m

4. **Extracting Data and Saving to a Text File**:
   ```sh
   python -m iceicedata.main -u "https://tempestwx.com/map/50515/65.1557/-16.47/6" -o output.txt

5. **Publishing Windrose Data to MQTT**:
   ```sh
   python -m iceicedata.main -u "https://tempestwx.com/map/50515/65.1557/-16.47/6" -m -w


## Requirements

To run this program on an Debian machine, you will need to have the following:

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

2. **Set Up a Virtual Environment (optional but recommended)**:
   ```sh
   python3 -m venv venv
   source venv/bin/activate

3. **Install the Required Dependencies**:
   ```sh
   pip install -r requirements.txt

4. **Install Mozilla Firefox (if not already installed)s**:
   ```sh
   sudo apt update
   sudo apt install firefox

5. **Install Geckodriver (the WebDriver for Firefox)**:
   ```sh
   wget https://github.com/mozilla/geckodriver/releases/download/v0.29.0/geckodriver-v0.29.0-linux64.tar.gz
   tar -xvzf geckodriver-v0.29.0-linux64.tar.gz
   sudo mv geckodriver /usr/local/bin/
[![Python application](https://github.com/douginoz/iceicedata/actions/workflows/python-app.yml/badge.svg)](https://github.com/douginoz/iceicedata/actions/workflows/python-app.yml)

# TempestWX Data Extractor

This program is designed to extract weather station data from any station displayed on the TempestWX map. It provides multiple options for outputting the extracted data, including JSON format, plain ASCII text, or publishing it to an MQTT server.

Apart from this paragraph, this program, structure, workflow, files, and the rest of this text were generated entirely by GPT-4 with prompts and iterative corrections. It is intended as a thought experiment and demonstration of using LLMs for code generation. It is not intended to be used publicly and will likely break as soon as the website format changes.

<sub><sup><span style="color:gray">This program, structure, workflow, files, and the rest of this text were generated entirely by GPT-4 with prompts and iterative corrections.</span></sup></sub>

## Features and Functionality

1. **URL Handling**:
   - The program accepts a URL pointing to an area on a TempestWX map that shows Tempest station installations.
   - If the map URL contains more than one station, the program scans for and lists all available placemarkers (weather stations) on the map, up to 50, allowing the user to select one.
   - If more than 50 placemarkers are found, the program prompts the user to zoom in closer to reduce the number of visible placemarkers.
   - Any location on Earth can be selected.

2. **Data Extraction**:
   - The program retrieves detailed weather data from the selected station, including air temperature, wind speed, wind direction, rain data, and other relevant meteorological parameters.

3. **Output Options**:
   - **JSON Output (`-j` or `--json`)**: Outputs the extracted data to a specified JSON file.
   - **Plain ASCII Output (`-o` or `--output`)**: Outputs the data in a human-readable format to a specified file or prints it to stdout if no filename is provided.
   - **MQTT Publishing (`-m` or `--mqtt`)**: Publishes the data to an MQTT server specified in a configuration file. If no file is specified, it looks for a default configuration file (`iceicedata.json`).
      - The MQTT configuration file can be generated using the -S option.

4. **MQTT Configuration**:
   - **Setup (`-S` or `--setup-mqtt`)**: Prompts the user to enter MQTT configuration details (server, port, username, password, root topic, windrose root topic) and saves them to a default configuration file (`iceicedata.json`). If the file already exists, it reads the existing values and allows the user to update them.
   - **Windrose Data (`-w` or `--windrose`)**: Optionally publishes windrose data to an MQTT topic. Winrose charts require 2 inputs - wind speed, in meters/second, and wind direction, as a compass bearing.  A separate MQSS topic name is used to minimize data being sent to the winrose application (grafana, Home Assistant etc). The topic name can be provided as an argument; if not, it uses the value from the configuration file.  This option can be used by itself or in conjunction with the -m (send all the other data to MQTT) option.

## Example Usage

1. **Setrting up MQTT Configuration**:
   ```sh
   python -m iceicedata.main -S

2. **Extracting JSON-formmated data to a file**:
   ```sh
   python -m iceicedata.main -u "https://tempestwx.com/map/50515/65.1557/-16.47/6" -j output.json

3. **Extracting Data and Publishing to a MQTT server**:
   ```sh
   python -m iceicedata.main -u "https://tempestwx.com/map/50515/65.1557/-16.47/6" -m

4. **Extracting Data and Saving to a Text File**:
   ```sh
   python -m iceicedata.main -u "https://tempestwx.com/map/50515/65.1557/-16.47/6" -o output.txt

5. **Publishing Windrose Data to MQTT**:
   ```sh
   python -m iceicedata.main -u "https://tempestwx.com/map/50515/65.1557/-16.47/6" -m -w


## Requirements

To run this program on an Debian machine, you will need to have the following:

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

2. **Set Up a Virtual Environment (optional but recommended)**:
   ```sh
   python3 -m venv venv
   source venv/bin/activate

3. **Install the Required Dependencies**:
   ```sh
   pip install -r requirements.txt

4. **Install Mozilla Firefox (if not already installed)s**:
   ```sh
   sudo apt update
   sudo apt install firefox

5. **Install Geckodriver (the WebDriver for Firefox)**:
   ```sh
   wget https://github.com/mozilla/geckodriver/releases/download/v0.29.0/geckodriver-v0.29.0-linux64.tar.gz
   tar -xvzf geckodriver-v0.29.0-linux64.tar.gz
   sudo mv geckodriver /usr/local/bin/
