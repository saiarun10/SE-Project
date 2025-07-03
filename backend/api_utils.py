from datetime import datetime
import pytz
import re
from flask import request
from flask.json.provider import DefaultJSONProvider
from datetime import date

class CustomJSONProvider(DefaultJSONProvider):
    """Custom JSON provider to handle date objects"""
    def default(self, obj):
        if isinstance(obj, date):
            return obj.isoformat()
        return super().default(obj)
    
def get_current_ist():
    """Returns the current datetime in Asia/Kolkata timezone."""
    ist = pytz.timezone('Asia/Kolkata')
    return datetime.now(ist)