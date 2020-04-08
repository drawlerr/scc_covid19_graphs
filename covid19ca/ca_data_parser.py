import datetime

import matplotlib.pyplot as plt
import pandas as pd

us_counties = pd.read_csv('us-counties.csv')


def get_county_data(counties):
    dfts = []
    for state, county in unpack_counties(counties):
        state_counties = us_counties[us_counties['state'] == state]
        df = state_counties[state_counties['county'] == county]
        dfts.append((state, county, df))
    return dfts


def parsedate(dstr):
    return datetime.datetime.strptime(dstr, "%Y-%m-%d")


def unpack_counties(counties):
    return [(c["state"], c["county"]) for c in counties]


def find_min_nonzero_date(dfs, cutoff):
    max_date = "9999-12-31"
    min_nonzero_date = max_date
    for df in dfs:
        df.sort_values('date')
        nonzero_cases = df[df['cases'] > cutoff]
        if not nonzero_cases.empty:
            min_nonzero_date = min(min_nonzero_date, nonzero_cases['date'].iloc[0])
    if min_nonzero_date != max_date:
        return min_nonzero_date
    return None


def normalize_dates(dfs):
    all_dates = dfs[0]['date']
    for df in dfs:
        all_dates.update(df['date'])
    for df in dfs:
        df.update(all_dates)


def plot_counties(dfts, filename):
    plt.switch_backend('Agg')
    plt.subplots()

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)

    dfs = [t[2] for t in dfts]
    min_nonzero_date = find_min_nonzero_date(dfs, 5)

    normalize_dates(dfs)

    for state, county, df in dfts:
        if min_nonzero_date:
            min_nz_df = df[df['date'] == min_nonzero_date]
            if not min_nz_df.empty:
                min_nonzero_idx = min_nz_df.index[0]
            else:
                min_nonzero_idx = 0
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
