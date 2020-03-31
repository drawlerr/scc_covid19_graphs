import csv
import numpy as np
import math
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.dates as mdates
import urllib.request

field_names = ['date','county','state','fips','cases','deaths']
covid_info = []
counties = set()

url = "https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv"
urllib.request.urlretrieve(url, 'us-counties.csv')


with open('us-counties.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if(row['state']=="California"):
            covid_info.append(row)
            counties.add(row['county'])

for county in counties:
    with open('{}.csv'.format(county), 'w') as f:
        writer = csv.DictWriter(f, fieldnames = field_names)
        writer.writeheader()
        for row in covid_info:
            if row['county'] == county:
                writer.writerow(row)

print(counties)

for county in counties:
    data = pd.read_csv('{}.csv'.format(county))
    date = data['date']
    cases = data['cases']

    plt.plot(date, cases)
    plt.gcf().autofmt_xdate()
    plt.ylabel('Cases (log scale)')
    plt.xlabel('Date')
    plt.title('Covid19 Cases: {} County'.format(county))
    fig, ax = plt.subplots(1,1)
    ax.plot(date,cases)

    ax.grid(True)
    ax.set_title('Covid19 Cases: {} County'.format(county))
    # rotates and right aligns the x labels, and moves the bottom of the
    # axes up to make room for them
    plt.xticks(date[::3],rotation=90)
    ax.set_yscale('log')
    plt.savefig('log_{}.png'.format(county))


    plt.close()