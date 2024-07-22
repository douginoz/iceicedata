import sqlite3
from contextlib import closing
import logging
import os
import sys
import pandas as pd
from datetime import datetime, time, timezone
import calendar

logger = logging.getLogger(__name__)

def create_database(database_file):
    database_dir = os.path.dirname(database_file)
    try:
        if not os.path.exists(database_dir):
            os.makedirs(database_dir, exist_ok=True)
            logger.debug(f"Created directory for database: {database_dir}")

        logger.debug(f"Connecting to SQLite database at '{database_file}'")
        conn = sqlite3.connect(database_file)

        with closing(conn.cursor()) as cursor:
            cursor.execute('''CREATE TABLE IF NOT EXISTS weather_data
                             (id INTEGER PRIMARY KEY AUTOINCREMENT,
                              station_id INTEGER,
                              station_name TEXT,
                              timestamp DATETIME,
                              timestamp_unix INTEGER,
                              air_density REAL,
                              air_temperature REAL,
                              station_pressure REAL,
                              brightness REAL,
                              delta_t REAL,
                              dew_point REAL,
                              feels_like REAL,
                              heat_index REAL,
                              lightning_strike_count INTEGER,
                              lightning_detected_last_3_hrs INTEGER,
                              lightning_distance_detected REAL,
                              lightning_last_detected REAL,
                              rain_intensity TEXT,
                              rain_accumulation_today REAL,
                              rain_accumulation_yesterday REAL,
                              rain_duration_today INTEGER,
                              rain_duration_yesterday INTEGER,
                              relative_humidity REAL,
                              sea_level_pressure REAL,
                              solar_radiation REAL,
                              timezone TEXT,
                              uv_index REAL,
                              wet_bulb_temperature REAL,
                              wind_speed REAL,
                              wind_chill REAL,
                              wind_direction REAL,
                              wind_gust REAL,
                              wind_lull REAL,
                              UNIQUE(station_id, timestamp_unix))''')
            logger.debug("Created weather_data table if it did not exist.")

            cursor.execute('''CREATE INDEX IF NOT EXISTS idx_weather_data_timestamp 
                              ON weather_data(timestamp)''')
            logger.debug("Created index on timestamp if it did not exist.")

            cursor.execute('''CREATE TABLE IF NOT EXISTS attribute_description
                             (attribute TEXT PRIMARY KEY,
                              description TEXT)''')
            logger.debug("Created attribute_description table if it did not exist.")

        conn.commit()
        logger.debug("Database created/modified successfully.")
        conn.close()
    except (sqlite3.Error, OSError) as e:
        logger.error(f"Error creating the database file at '{database_file}': {e}")
        print(f"Error: Unable to create the database file at '{database_file}'. Please check the file path and permissions.")
        sys.exit(1)

def insert_data_into_database(database_file, data, attribute_descriptions):
    logger.debug(f"Connecting to database '{database_file}' for data insertion.")
    conn = sqlite3.connect(database_file)

    with closing(conn.cursor()) as cursor:
        logger.debug("Inserting data into weather_data table: %s", data)

        # Handle date-only timestamp
        timestamp_str = data['timestamp']['value']
        try:
            # Parse date only
            date_only = datetime.strptime(timestamp_str, "%m/%d/%Y").date()
            # Combine with midnight time
            timestamp = datetime.combine(date_only, time.min)
        except ValueError:
            logger.error(f"Unable to parse timestamp: {timestamp_str}")
            raise

        formatted_timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S")
        
        # Generate Unix timestamp
        timestamp_unix = calendar.timegm(timestamp.timetuple())

        try:
            cursor.execute('''INSERT OR REPLACE INTO weather_data
                             (station_id, station_name, timestamp, timestamp_unix, air_density, air_temperature, station_pressure, brightness, delta_t, dew_point, feels_like, heat_index, 
                              lightning_strike_count, lightning_detected_last_3_hrs, lightning_distance_detected, lightning_last_detected, rain_intensity, 
                              rain_accumulation_today, rain_accumulation_yesterday, rain_duration_today, rain_duration_yesterday, relative_humidity, 
                              sea_level_pressure, solar_radiation, timezone, uv_index, wet_bulb_temperature, wind_speed, 
                              wind_chill, wind_direction, wind_gust, wind_lull)
                             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                             (data['station_id'], data['station_name'], formatted_timestamp, timestamp_unix, 
                              data['air_density']['value'], data['air_temperature']['value'], data['station_pressure']['value'],
                              data['brightness']['value'], data['delta_t']['value'], data['dew_point']['value'], data['feels_like']['value'], data['heat_index']['value'],
                              data['lightning_strike_count']['value'], data['lightning_detected_last_3_hrs']['value'], data['lightning_distance_detected']['value'],
                              data['lightning_last_detected']['value'], data['rain_intensity']['value'], data['rain_accumulation_today']['value'],
                              data['rain_accumulation_yesterday']['value'], data['rain_duration_today']['value'], data['rain_duration_yesterday']['value'],
                              data['relative_humidity']['value'], data['sea_level_pressure']['value'], data['solar_radiation']['value'], 
                              data['timezone']['value'], data['uv_index']['value'], data['wet_bulb_temperature']['value'],
                              data['wind_speed']['value'], data['wind_chill']['value'], data['wind_direction']['value'], data['wind_gust']['value'],
                              data['wind_lull']['value']))
            logger.debug("Weather data inserted successfully.")
        except sqlite3.IntegrityError as e:
            logger.warning(f"Duplicate data detected for station {data['station_id']} at timestamp {formatted_timestamp}. Skipping insertion.")

        # Insert attribute descriptions
        logger.debug("Attribute descriptions to be inserted: %s", attribute_descriptions)
        for attribute, description in attribute_descriptions.items():
            logger.debug("Inserting attribute description for '%s': '%s'", attribute, description)
            cursor.execute("INSERT OR REPLACE INTO attribute_description (attribute, description) VALUES (?, ?)", (attribute, description))
            logger.debug("Attribute description inserted successfully.")

    conn.commit()
    logger.debug("Data insertion committed to the database.")
    conn.close()

def check_database_integrity(database_file):
    logger.debug(f"Checking integrity of database '{database_file}'.")
    conn = sqlite3.connect(database_file)

    with closing(conn.cursor()) as cursor:
        cursor.execute("PRAGMA foreign_key_check;")
        if list(cursor):
            logger.error("Database integrity check failed. Please repair the database.")
            return False
    conn.close()
    logger.debug("Database integrity check passed.")
    return True

def get_data_range(database_file):
    logger.debug(f"Retrieving data range from '{database_file}'")
    conn = sqlite3.connect(database_file)
    
    query = "SELECT MIN(timestamp), MAX(timestamp) FROM weather_data"
    
    cursor = conn.cursor()
    cursor.execute(query)
    start_date, end_date = cursor.fetchone()
    
    conn.close()
    
    if start_date and end_date:
        # SQLite stores DATETIME as strings, so we need to parse them
        start_date = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
        end_date = datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
        logger.debug(f"Data range: {start_date} to {end_date}")
    else:
        logger.warning("No data found in the database")
        start_date, end_date = None, None
    
    return start_date, end_date

def get_data_for_report(database_file, start_date, end_date):
    logger.debug(f"Retrieving data from '{database_file}' for report from {start_date} to {end_date}")
    conn = sqlite3.connect(database_file)
    
    query = '''
    SELECT timestamp, air_temperature, station_pressure, relative_humidity, wind_speed
    FROM weather_data
    WHERE timestamp BETWEEN ? AND ?
    ORDER BY timestamp
    '''
    
    df = pd.read_sql_query(query, conn, params=(start_date, end_date))
    
    conn.close()
    
    if df.empty:
        logger.warning("No data found for the specified date range")
    else:
        logger.debug(f"Retrieved {len(df)} rows of data")
    
    return df

def get_all_data(database_file):
    logger.debug(f"Retrieving all data from '{database_file}'")
    conn = sqlite3.connect(database_file)
    
    query = "SELECT * FROM weather_data ORDER BY timestamp"
    
    df = pd.read_sql_query(query, conn)
    
    conn.close()
    
    if df.empty:
        logger.warning("No data found in the database")
    else:
        logger.debug(f"Retrieved {len(df)} rows of data")
    
    return df

def get_attribute_descriptions(database_file):
    logger.debug(f"Retrieving attribute descriptions from '{database_file}'")
    conn = sqlite3.connect(database_file)
    
    query = "SELECT * FROM attribute_description"
    
    df = pd.read_sql_query(query, conn)
    
    conn.close()
    
    if df.empty:
        logger.warning("No attribute descriptions found in the database")
    else:
        logger.debug(f"Retrieved {len(df)} attribute descriptions")
    
    return df.set_index('attribute')['description'].to_dict()