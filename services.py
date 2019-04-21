import os
import glob
import pickle
import pytz
from dateutil import parser
from datetime import datetime
from datetime import timezone
from datetime import timedelta


def convert_datetime(_datetime):
    try:
        _datetime = datetime.fromtimestamp(_datetime, tz=pytz.utc)
    except TypeError:
        _datetime = _datetime
    if isinstance(_datetime, str):
        _datetime = parser.parse(_datetime)
    return _datetime


def filter_last_months(_dict, time_marker, months):
    qty_days_in_year, qty_months_in_year = 365, 12
    now = datetime.now(timezone.utc)
    past_time_point = now - timedelta(months * qty_days_in_year //
                                      qty_months_in_year)
    if isinstance(_dict, dict):
        created_time = convert_datetime(_dict[time_marker])
        if created_time >= past_time_point:
            return _dict


def merge_list(lst_lst):
    _all = []
    [_all.extend(lst) for lst in lst_lst]
    return _all


def storage_picle_io(in_data, picle_file_pathname):
    """DATA: input/output Picle file."""
    if not os.path.exists(picle_file_pathname):
        with open(picle_file_pathname, 'wb') as f:
            pickle.dump(in_data, f)
        return in_data
    else:
        with open(picle_file_pathname, 'rb') as f:
            out_data = pickle.load(f)
        return out_data


def delete_pickle_files():
    try:
        for pathname in glob.glob(r'*.pickle'):
            if os.path.exists(pathname):
                os.remove(pathname)
    except OSError:
        pass



