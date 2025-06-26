from datetime import datetime
import pytz

def get_current_ist():
    """Returns the current datetime in Asia/Kolkata timezone."""
    return datetime.now(pytz.timezone("Asia/Kolkata"))

