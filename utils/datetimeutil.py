import pytz
from pytz import timezone
from datetime import timedelta
from dateutil import parser

tpe_tz = timezone('Asia/Taipei')


def utc_to_tpe(d):
    """
    Convert UTC datetime to TPE datetime (with timezone info)
    """
    return pytz.utc.localize(d).astimezone(tpe_tz)


def tpe_to_utc_str(d):
    """
    Convert TPE datetime to UTC datetime
    """
    return tpe_tz.localize(d).astimezone(pytz.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

def compare_time_arrange_mins(compare_one, compare_two, mins=1) -> bool:
    # '2024-02-04T10:14:54Z'
    dt = parser.parse(compare_one)
    dt_actions = parser.parse(compare_two)
    result = dt_actions - dt
    return result > timedelta(minutes=mins)