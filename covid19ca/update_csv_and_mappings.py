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
unknowns = set()

with open('us-counties.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        place = f"{row['state']} - {row['county']}"
        try:
            fips = int(row['fips'])
        except ValueError:
            if row['county'] == "New York City":
                fips = 36061
            else:
                unknowns.add(place)
                continue
        fips_county_dict[place] = fips

unknowns_list = "\n" + "\n".join(sorted(unknowns))
print(f"{len(unknowns)} counties with missing FIPS IDs: {unknowns_list}")
fips_county_dict = OrderedDict(sorted(fips_county_dict.items()))

with open(os.path.join(STATIC_FOLDER, 'fips_county_mapping.json'), 'w') as f:
    json.dump(fips_county_dict, f, separators=(',\n', ': '))
