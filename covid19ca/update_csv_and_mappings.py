import os
import csv
import json
import urllib.request

STATIC_FOLDER = os.path.join('static')

url = "https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv"
urllib.request.urlretrieve(url, 'us-counties.csv')


state_county_dict ={}

with open('us-counties.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row['state'] in state_county_dict.keys():
            state_county_dict[row['state']].add(row['county'])
        else:

            state_county_dict[row['state']] = {row['county']}

for key in state_county_dict.keys():
    state_county_dict[key] = list(state_county_dict[key])

county_states_mapping = []
with open(os.path.join(STATIC_FOLDER, 'county_state_mapping'), 'w') as f:
    f.write(json.dumps(state_county_dict))
