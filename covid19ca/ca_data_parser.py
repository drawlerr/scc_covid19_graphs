import csv
import numpy as np
import math
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.dates as mdates
import urllib.request

field_names = ['date','county','state','fips','cases','deaths']
counties = set()




norcal_counties = {'Santa Cruz': 'California', 'Santa Clara': 'California',  'Napa': 'California',
                   'Alameda': 'California', 'San Mateo': 'California',
                   'San Francisco': 'California',
                   'Marin': 'California', 'Solano': 'California','Contra Costa': 'California'}

socal_counties = {'Ventura' :'California',  'San Diego':'California', 'Kern':'California',
                  'Los Angeles':'California', 'San Bernardino' :'California', 'Riverside':'California',
                  'Orange':'California', 'Kings':'California'}

md_va_dc_counties = {'Carroll': 'Maryland', 'Frederick': 'Maryland','District of Columbia':'District of Columbia',  "Prince George's": 'Maryland', 'Arlington': 'Virginia', 'Fairfax': 'Virginia'}




def get_county_data_from_csv(counties):
    county_info =[]
    with open('us-counties.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            for county, state in counties.items():
                if row['state']== state and row['county'] == county:
                    county_info.append(row)
    return county_info


def get_date_range(county_info):
    date_set = set()
    for row in county_info:
        date_set.add(row['date'])
    return date_set

def create_count_csv(counties, covid_info, date_set):
    for county in counties:
        county_info = []
        dates_added = set()
        for row in covid_info:
            if row['county'] == county:
                dates_added.add(row['date'])
                county_info.append(row)

        for date in date_set:
            if date not in dates_added:
                row = {
                    'date': date,
                    'county': county,
                    'state': "California",
                    'fips': '00000', #this can be nonsense for now
                    'cases': 0,
                    'deaths': 0
                }
                county_info.append(row)
        county_info = sorted(county_info, key = lambda i: i['date'])
        with open('{}.csv'.format(county), 'w') as f:
            writer = csv.DictWriter(f, fieldnames=field_names)
            writer.writeheader()
            for row in county_info:
                writer.writerow(row)

def plot_counties(counties, filename):
    plt.switch_backend('Agg')
    plt.subplots()

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)

    for county, state in counties.items():
        data = pd.read_csv('{}.csv'.format(county))
        data.sort_values('date')
        cases = data['cases']
        date = data['date']
        plt.gcf().autofmt_xdate()
        ax.plot(date, cases, label="{},{}".format(county, state))


        # rotates and right aligns the x labels, and moves the bottom of the
        # axes up to make room for them

    plt.grid(True)
    plt.legend()
    plt.title("COVID19 Cases")
    plt.ylabel('Cases (log scale)')
    plt.xlabel('Date')
    plt.xticks(date[::3],rotation=90)
    plt.yscale('log')

    plt.savefig(filename)


def main():
    counties = norcal_counties
    county_info =get_county_data_from_csv(counties)
    date_range = get_date_range(county_info)
    create_count_csv(counties.keys(), county_info, date_range)
    plot_counties(counties, 'norcal.png')

if __name__=="__main__":
    main()