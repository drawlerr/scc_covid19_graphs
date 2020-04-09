import matplotlib.pyplot as plt
import pandas as pd

us_counties = pd.read_csv('us-counties.csv',
                          index_col="date",
                          parse_dates=True)

NYC_COUNTY = "New York City"
NYC_FIPS = 36061


class NoDataAvailableException(BaseException):
    pass


def get_county_data(counties):
    dfs = []
    for fips in counties:
        df = us_counties[us_counties['fips'] == fips]
        if df.empty:
            continue
        dfs.append(df)
    return dfs


def find_min_nonzero_date(dfs, cutoff):
    max_date = pd.Timestamp.max
    min_nonzero_date = max_date
    for df in dfs:
        df.sort_values('date')
        nonzero_cases = df[df['cases'] > cutoff]
        if not nonzero_cases.empty:
            min_nonzero_date = min(min_nonzero_date, nonzero_cases.index[0])
    if min_nonzero_date != max_date:
        return min_nonzero_date
    return None


def combine_date_ranges(dfs):
    dr = dfs[0].index.to_series()
    for df in dfs[1:]:
        dr = dr.append(df.index.to_series())
    dr = dr.sort_values().unique()
    return pd.Series(dr)


def plot_counties(dfs, filename):
    plt.switch_backend('Agg')
    plt.subplots()
    ax = plt.figure().add_subplot()

    min_nonzero_date = find_min_nonzero_date(dfs, 5)
    daterange = combine_date_ranges(dfs)

    for df in dfs:
        county = df.head(1)['county'].values[0]
        state = df.head(1)['state'].values[0]

        if min_nonzero_date:
            date_truncated_df = df.loc[df.index > min_nonzero_date]
            daterange = daterange.loc[lambda d: d > min_nonzero_date]
        else:
            date_truncated_df = df
        cases = date_truncated_df['cases']
        date = date_truncated_df.index
        plt.gcf().autofmt_xdate()
        ax.plot(date, cases, label="{},{}".format(county, state))
    plt.grid(True)
    plt.legend()
    plt.title("COVID19 Cases")
    plt.ylabel('Cases (log scale)')
    plt.xlabel('Date')
    plt.xticks(daterange[::3], rotation=90)
    plt.yscale('log')

    plt.savefig(filename)
