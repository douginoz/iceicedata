import pytz
from datetime import datetime

def convert_wind_speed_to_mps(speed):
    try:
        return round(float(speed) * 0.27778, 2)
    except ValueError:
        return speed  # Return the original speed if conversion fails

def split_value_and_unit(value):
    parts = value.split(' ')
    numeric_value = parts[0]
    unit = ' '.join(parts[1:]) if len(parts) > 1 else None
    return numeric_value, unit

def convert_timestamp_to_unix_ms(timestamp_str, timezone_str):
    try:
        local_tz = pytz.timezone(timezone_str)
        local_dt = datetime.strptime(timestamp_str, '%m/%d/%Y %I:%M:%S %p')
        local_dt = local_tz.localize(local_dt, is_dst=None)
        unix_time_ms = int(local_dt.timestamp() * 1000)
        return unix_time_ms
    except Exception as e:
        return None

def convert_compass_to_degrees(direction):
    compass_to_degrees = {
        "N": 0, "NNE": 22.5, "NE": 45, "ENE": 67.5,
        "E": 90, "ESE": 112.5, "SE": 135, "SSE": 157.5,
        "S": 180, "SSW": 202.5, "SW": 225, "WSW": 247.5,
        "W": 270, "WNW": 292.5, "NW": 315, "NNW": 337.5
    }
    return compass_to_degrees.get(direction, None)

def validate_url(url):
    logger = logging.getLogger()
    logger.debug("Validating URL: %s", url)
    if "tempestwx.com/map/" not in url:
        raise ValueError("Invalid URL format. Please provide a valid TempestWX URL.")
    return url

def extract_coordinates(url):
    parts = url.split('/')
    if len(parts) >= 7:
        latitude = parts[-3]
        longitude = parts[-2]
        zoom = parts[-1]
        return latitude, longitude, zoom
    else:
        raise ValueError("URL does not contain valid coordinates.")

def get_station_id_from_url(url):
    parts = url.split('/')
    if len(parts) >= 7 and parts[-4].isdigit():
        return parts[-4]
    return None
