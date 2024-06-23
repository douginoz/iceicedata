[![Python application](https://github.com/douginoz/iceicedata/actions/workflows/python-app.yml/badge.svg)](https://github.com/douginoz/iceicedata/actions/workflows/python-app.yml)

# TempestWX Data Extractor

This program is designed to extract weather station data from any station displayed on the TempestWX map. It provides multiple options for outputting the extracted data, including JSON format, plain ASCII text, or publishing it to an MQTT server.  This program and this text was generated entirely by GPT4o with prompts and iterative corrections.  It is intended as a thought experiment and demonstration of using LLMs for code generation.  It is not intended to be used publically and will likely break as soon as the website format changes.

## Features and Functionality

1. **URL Handling**:
   - The program accepts a URL pointing to a specific area on the TempestWX map. The URL can be in one of two formats:
     - `https://tempestwx.com/map/{latitude}/{longitude}/{zoom}`: This format does not include a station ID.
     - `https://tempestwx.com/map/{stationID}/{latitude}/{longitude}/{zoom}`: This format includes a station ID.
   - If the URL does not contain a station ID, the program scans for available placemarkers (weather stations) on the map, allowing the user to select one.
   - If more than 50 placemarkers are found, the program prompts the user to zoom in closer to reduce the number of visible placemarkers.

2. **Data Extraction**:
   - The program uses Selenium WebDriver to interact with the TempestWX website.
   - It retrieves detailed weather data from the selected station, including air temperature, wind speed, wind direction, and other relevant meteorological parameters.

3. **Output Options**:
   - **JSON Output (`-j` or `--json`)**: Outputs the extracted data to a specified JSON file.
   - **Plain ASCII Output (`-o` or `--output`)**: Outputs the data in a human-readable format to a specified file or prints it to stdout if no filename is provided.
   - **MQTT Publishing (`-m` or `--mqtt`)**: Publishes the data to an MQTT server specified in a configuration file. If no file is specified, it looks for a default configuration file (`tempestwx.json`).

4. **MQTT Configuration**:
   - **Setup (`-s` or `--setup-mqtt`)**: Prompts the user to enter MQTT configuration details (server, port, username, password, root topic, windrose root topic) and saves them to a default configuration file (`tempestwx.json`). If the file already exists, it reads the existing values and allows the user to update them.
   - **Windrose Data (`-w` or `--windrose`)**: Optionally publishes windrose data to an MQTT topic. The topic name can be provided as an argument; if not, it uses the value from the configuration file.

5. **Description in Help Message**:
   - The program description and usage instructions are included in the help message, which is displayed when the `-h` or `--help` option is used. It explains how to use the various options and parameters.

## Program Workflow

1. **Initialization**:
   - The program starts by parsing command-line arguments.
   - It validates the provided URL and extracts coordinates and, if present, the station ID.

2. **Web Interaction**:
   - The program initializes the Selenium WebDriver and navigates to the specified URL.
   - If the station ID is not in the URL, it scans for placemarkers and prompts the user to select one.

3. **Data Retrieval**:
   - Once the station ID is determined, the program constructs a URL with the station ID and navigates to it.
   - It retrieves detailed weather data from the station-detail section of the webpage.

4. **Data Output**:
   - The program outputs the data according to the specified options:
     - Saves to a JSON file if `-j` is used.
     - Saves to a plain ASCII file or prints to stdout if `-o` is used.
     - Publishes to an MQTT server if `-m` is used.
   - If windrose data is to be published (`-w`), it uses the topic name provided as an argument or from the configuration file.

## Example Usage

1. **Setup MQTT Configuration**:
   ```sh
   python iceicedata.py -s
2. **Extract Data and Save to JSON**:
   ```sh
   python iceicedata.py -j output.json https://tempestwx.com/map/50515/65.1557/-16.47/6 
3. **Extract Data and Publish to MQTT:**:
   ```sh
   python iceicedata.py -m https://tempestwx.com/map/50515/65.1557/-16.47/6 
4. **Extract Data and Save to Text File:**:
   ```sh
   python iceicedata.py -o output.txt https://tempestwx.com/map/50515/65.1557/-16.47/6 
5. **Publish Windrose Data to MQTT:**:
   ```sh
   python iceicedata.py -m -w WindroseTopic/ https://tempestwx.com/map/50515/65.1557/-16.47/6 


## Requirements

To run this program on an Ubuntu machine, you will need to have the following:

1. **Python 3.6 or higher**: Ensure Python is installed and accessible from the command line.
2. **Selenium WebDriver**: Required for web scraping.
3. **Geckodriver**: The WebDriver for Firefox.
4. **Mozilla Firefox**: The web browser used by Selenium.
5. **Paho MQTT**: A Python library for MQTT communication.

## Installation Steps

Follow these steps to install the necessary dependencies and set up the environment:

1. **Update Package List**: First, update the package list on your Ubuntu machine to ensure you have the latest information on the newest versions of packages and their dependencies.

2. **Install Python 3**: Install Python 3 and pip (Python's package installer) if they are not already installed on your system.

3. **Install Mozilla Firefox**: Install the Mozilla Firefox web browser, which is required by Selenium WebDriver for web scraping.

4. **Install Geckodriver**: Download and install Geckodriver, the WebDriver for Firefox. Extract the downloaded tar file and move the Geckodriver binary to `/usr/local/bin` to make it accessible system-wide.

5. **Install Selenium and Paho MQTT**: Use pip to install the Selenium and Paho MQTT libraries, which are required for web scraping and MQTT communication, respectively.
