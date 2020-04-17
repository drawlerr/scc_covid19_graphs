#!/usr/bin/env python3
from datetime import datetime
import os
import csv
import json
import urllib.request
from collections import OrderedDict

STATIC_FOLDER = os.path.join('static')

url = "https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv"
urllib.request.urlretrieve(url, 'us-counties.csv')

fips_county_dict = {}
latest_date = datetime.min
unknowns = set()

with open('us-counties.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        state = row['state']
        county = row['county']
        place = f"{state} - {county}"
        try:
            fips = int(row['fips'])
        except ValueError:
            if county == "New York City":
                fips = 36061
            elif state == "Missouri" and county == "Kansas City":
                fips = 29095
            else:
                unknowns.add(place)
                continue
        fips_county_dict[place] = fips
        date = datetime.strptime(row['date'], "%Y-%m-%d")
        latest_date = max(latest_date, date)

print(f"Latest date: {latest_date.strftime('%Y-%m-%d')}")
unknowns_list = "\n" + "\n".join(sorted(unknowns))
print(f"{len(unknowns)} counties with missing FIPS IDs: {unknowns_list}")
fips_county_dict = OrderedDict(sorted(fips_county_dict.items()))

with open(os.path.join(STATIC_FOLDER, 'fips_county_mapping.json'), 'w') as f:
    json.dump(fips_county_dict, f, separators=(',\n', ': '))
