#!/usr/bin/env python3
import os
import csv
import json
import urllib.request
from collections import OrderedDict

STATIC_FOLDER = os.path.join('static')

url = "https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv"
urllib.request.urlretrieve(url, 'us-counties.csv')

fips_county_dict = {}

with open('us-counties.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        try:
            fips = int(row['fips'])
        except ValueError:
            if row['county'] == "New York City":
                fips = 36061
            else:
                continue
        state = row['state']
        county = row['county']
        name = f"{state} - {county}"
        fips_county_dict[name] = fips

fips_county_dict = OrderedDict(sorted(fips_county_dict.items()))

with open(os.path.join(STATIC_FOLDER, 'fips_county_mapping.json'), 'w') as f:
    json.dump(fips_county_dict, f, separators=(',\n', ': '))
