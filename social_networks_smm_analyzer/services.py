import os
import pytz
import json
from pathlib import Path
from dateutil import parser
from datetime import datetime
from datetime import timezone
from datetime import timedelta


test_switch_var = []


def test_switch(mode):
    if mode is True:
        test_switch_var.append(mode)
    else:
        try:
          test_switch_var.pop()
        except IndexError:
          pass


def storage_json_io_decorator(storage_folder, storage_file_pathname):
    parent_path = Path(os.path.abspath(storage_folder)).parent.parent
    pathname = os.path.join(parent_path, storage_folder, storage_file_pathname)
    def memoize(func):
        def decorate(*args, **kwargs):
            if test_switch_var:
                try:
                    with open(pathname, 'r', encoding='utf-8') as fl:
                        var_data = json.load(fl)
                    return var_data
                except (FileNotFoundError, IOError):
                    var_data = func(*args, **kwargs)
                    with open(pathname, 'w', encoding='utf-8') as fl:
                        json.dump(var_data, fl, ensure_ascii=False)
                    return var_data
            else:
                return func(*args, **kwargs)
        return decorate
    return memoize


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

