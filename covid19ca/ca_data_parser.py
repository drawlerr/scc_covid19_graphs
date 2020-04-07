import csv
import datetime

import matplotlib.pyplot as plt
import pandas as pd

field_names = ['date', 'county', 'state', 'fips', 'cases', 'deaths']

norcal_counties = {'Santa Cruz': 'California', 'Santa Clara': 'California', 'Napa': 'California',
                   'Alameda': 'California', 'San Mateo': 'California',
                   'San Francisco': 'California',
                   'Marin': 'California', 'Solano': 'California', 'Contra Costa': 'California'}

socal_counties = {'Ventura': 'California', 'San Diego': 'California', 'Kern': 'California',
                  'Los Angeles': 'California', 'San Bernardino': 'California', 'Riverside': 'California',
                  'Orange': 'California', 'Kings': 'California'}

md_va_dc_counties = {'Carroll': 'Maryland', 'Frederick': 'Maryland', 'District of Columbia': 'District of Columbia',
                     "Prince George's": 'Maryland', 'Arlington': 'Virginia', 'Fairfax': 'Virginia'}


def filter_by_selected_counties(rows, counties):
    filtered_rows = []
    for row in rows:
        for state, county in unpack_counties(counties):
            if row['state'] == state and row['county'] == county:
                filtered_rows.append(row)
    return filtered_rows


def get_county_data_from_csv(counties):
    with open('us-counties.csv', 'r') as f:
        reader = csv.DictReader(f)
        return filter_by_selected_counties(reader, counties)


def parsedate(dstr):
    return datetime.datetime.strptime(dstr, "%Y-%m-%d")


def get_date_range(county_info):
    date_set = set()
    for row in county_info:
        date_set.add(parsedate(row["date"]))
    return sorted(date_set)


def create_count_csv(counties, covid_info, date_set):
    for state, county in unpack_counties(counties):
        county_info = []
        dates_added = set()
        for row in covid_info:
            if row['county'] == county and row['state'] == state:
                dates_added.add(parsedate(row["date"]))
                county_info.append(row)

        for date in sorted(date_set):
            if date not in dates_added:
                row = {
                    'date': date.strftime("%Y-%m-%d"),
                    'county': county,
                    'state': state,
                    'fips': '00000',  # this can be nonsense for now
                    'cases': 0,
                    'deaths': 0
                }
                county_info.append(row)
        county_info = sorted(county_info, key=lambda i: i['date'])
        with open(f'{state}-{county}.csv', 'w') as f:
            writer = csv.DictWriter(f, fieldnames=field_names)
            writer.writeheader()
            for row in county_info:
                writer.writerow(row)


def unpack_counties(counties):
    return [(c["state"], c["county"]) for c in counties]


MAX_DATE = "9999-12-31"


def plot_counties(counties, filename):
    plt.switch_backend('Agg')
    plt.subplots()

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    min_nonzero_date = MAX_DATE

    dftuples = []
    for state, county in unpack_counties(counties):
        df = pd.read_csv(f'{state}-{county}.csv')
        df.sort_values('date')
        dftuples.append((state, county, df))
        nonzero_cases = df[df['cases'] > 5]
        if not nonzero_cases.empty:
            min_nonzero_date = min(min_nonzero_date, nonzero_cases['date'].iloc[0])
    for state, county, df in dftuples:
        if min_nonzero_date != MAX_DATE:
            min_nonzero_idx = df[df['date'] == min_nonzero_date].index[0]
        else:
            min_nonzero_idx = 0
        cases = df['cases'][min_nonzero_idx:]
        date = df['date'][min_nonzero_idx:]
        plt.gcf().autofmt_xdate()
        ax.plot(date, cases, label="{},{}".format(county, state))
    plt.grid(True)
    plt.legend()
    plt.title("COVID19 Cases")
    plt.ylabel('Cases (log scale)')
    plt.xlabel('Date')
    plt.xticks(date[::3], rotation=90)
    plt.yscale('log')

    plt.savefig(filename)


def main():
    counties = norcal_counties
    county_info = get_county_data_from_csv(counties)
    date_range = get_date_range(county_info)
    create_count_csv(counties.keys(), county_info, date_range)
    plot_counties(counties, 'norcal.png')


if __name__ == "__main__":
    main()
