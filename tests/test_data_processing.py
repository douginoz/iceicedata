from datetime import datetime
import pytz

def convert_timestamp_to_unix_ms(timestamp_str, timezone_str):
    try:
        tz = pytz.timezone(timezone_str)
        dt = datetime.strptime(timestamp_str, '%m/%d/%Y %I:%M:%S %p')
        dt = tz.localize(dt)
        return int(dt.timestamp() * 1000)
    except Exception as e:
        print(f"Error converting timestamp: {e}")
        return None
