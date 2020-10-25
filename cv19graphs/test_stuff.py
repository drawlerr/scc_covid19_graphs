from datetime import datetime, timedelta
from unittest.mock import patch

import numpy
import pandas as pd

from cv19graphs.ca_data_parser import decimate_ticks, combine_date_ranges, get_county_data


def setup_module(_):
    pd.set_option('display.max_rows', 500)


def test_combine_date_ranges():
    dfs = get_county_data([6073, 17031])
    drs = [df.date for df in dfs]
    combined = combine_date_ranges(dfs)
    for dr in drs:
        for date in dr.array.date:
            assert date in combined.array.date


def test_decimate_ticks_current():
    df = get_county_data([17031])[0]
    dr = df.date
    last_day = dr.array.date[-1]
    ticks = decimate_ticks(dr)
    assert ticks[-1] == last_day
    second_to_last = ticks[-2]
    assert last_day - second_to_last >= numpy.timedelta64(7, 'D')

    # if data is up-to-date, don't repeat the test
    if datetime.today() == last_day:
        return
    last_day = datetime.today()
    dr = dr.append(pd.Series([last_day]))
    ticks = decimate_ticks(dr)
    assert ticks[-1] == last_day.date()
    second_to_last = ticks[-2]
    assert last_day.date() - second_to_last >= timedelta(days=7)
