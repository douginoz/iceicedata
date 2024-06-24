import pytz
from datetime import datetime

def split_value_and_unit(value):
    parts = value.split(' ')
    numeric_value = parts[0]
    unit = ' '.join(parts[1:]) if len(parts) > 1 else None
    return numeric_value, unit

def convert_wind_speed_to_mps(speed):
    try:
        local_tz = pytz.timezone(timezone_str)
        local_dt = datetime.strptime(timestamp_str, '%m/%d/%Y %I:%M:%S %p')
        local_dt = local_tz.localize(local_dt, is_dst=None)
        unix_time_ms = int(local_dt.timestamp() * 1000)
        return unix_time_ms
        return round(float(speed) * 0.27778, 2)
    except ValueError as e:
        return speed

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
