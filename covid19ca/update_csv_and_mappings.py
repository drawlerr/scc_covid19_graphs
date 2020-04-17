#!/usr/bin/env python3
import gzip
from datetime import datetime
import os
import csv
import json
from urllib.request import Request, urlopen
from collections import OrderedDict

STATIC_FOLDER = os.path.join('static')


def get_url(url, filename):
    req = Request(url)
    req.headers = {
        'Accept-Encoding': 'gzip, deflate',
    }
    response = urlopen(req)
    encoding = response.info().get("Content-Encoding")
    if encoding == "gzip":
        print("gzipped response")
        orig = response.read()
        data = gzip.decompress(orig)
        print(f"orig:{len(orig)}  gunzip:{len(data)} ratio:{len(orig)*100/len(data):.2f}")
    elif encoding == 'deflate':
        print("deflate response")
        data = response.read()
    elif encoding:
        raise Exception(f'Encoding type <{encoding}> unknown')
    else:
        print("non-encoded response")
        data = response.read()
    with open(filename, "wb") as f:
        f.write(data)


url = "https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv"
get_url(url, "us-counties.csv")

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
