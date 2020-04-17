import matplotlib.pyplot as plt
import pandas as pd

NYC_COUNTY = "New York City"
NYC_FIPS = 36061
CHARTS = {
    "cases": {"chart_title": "COVID19 Total Cases",
              "yscale": "log",
              "ylabel": "Total Cases (log scale)"},
    "deaths": {"chart_title": "COVID19 Total Deaths",
               "ylabel": "Total Deaths"},
    "new_cases": {"chart_title": "COVID19 New Cases",
                  "ylabel": "New Cases"},
    "new_deaths": {"chart_title": "COVID19 New Deaths",
                   "ylabel": "New Deaths"},
}
DEFAULT_CHART_TYPE = "cases"

us_counties = pd.DataFrame()
latest_date = ""


def reload_us_counties(filename="us-counties.csv"):
    global us_counties, latest_date
    counties = pd.read_csv(filename,
                           dtype={"county": "string",
                                  "state": "string",
                                  "fips": "Int32",
                                  "cases": "Int32",
                                  "deaths": "Int32"},
                           parse_dates=[0])
    # fix empty FIPS for NYC
    counties.loc[(counties.county == NYC_COUNTY) & (counties.fips.isnull()), 'fips'] = NYC_FIPS

    # add "new_cases" computed column
    deltas = counties.groupby(by=["state", "county"]).diff(axis=1).convert_dtypes().fillna(0)
    counties["new_cases"] = deltas.cases
    counties["new_deaths"] = deltas.deaths

    latest_date = counties.date.tail(1).dt.strftime("%Y-%m-%d").values[0]
    us_counties = counties


reload_us_counties()


class NoDataAvailableException(BaseException):
    pass


def get_county_data(counties):
    dfs = []
    for fips in counties:
        df = us_counties.loc[us_counties.fips == fips]
        if df.empty:
            continue
        dfs.append(df)
    return dfs


def find_min_nonzero_date(dfs, cutoff):
    max_date = pd.Timestamp.max
    max_df_date = pd.Timestamp.min
    min_nonzero_date = max_date
    for df in dfs:
        df.sort_values('date')
        max_df_date = max(max_df_date, df.date.max())
        nonzero_cases = df[df.cases > cutoff]
        if not nonzero_cases.empty:
            min_nonzero_date = min(min_nonzero_date, nonzero_cases.head(1).date.values[0])
    if min_nonzero_date != max_date and min_nonzero_date != max_df_date:
        return min_nonzero_date
    return None


def combine_date_ranges(dfs):
    dr = dfs[0].date
    for df in dfs[1:]:
        dr = dr.append(df.date)
    dr = dr.sort_values().unique()
    return pd.Series(dr)


def plot_counties(dfs, chart_type, filename):
    plt.switch_backend('Agg')
    plt.subplots()
    ax = plt.figure().add_subplot()

    if not chart_type:
        chart_type = DEFAULT_CHART_TYPE
    if chart_type not in CHARTS:
        raise ValueError("Invalid chart type!")
    chart = CHARTS[chart_type]
    min_nonzero_date = find_min_nonzero_date(dfs, 5)
    if not min_nonzero_date:
        min_nonzero_date = find_min_nonzero_date(dfs, 1)
    daterange = combine_date_ranges(dfs)

    for df in dfs:
        county = df.head(1).county.values[0]
        state = df.head(1).state.values[0]

        if min_nonzero_date:
            date_truncated_df = df.loc[df.date >= min_nonzero_date]
            daterange = daterange.loc[lambda d: d >= min_nonzero_date]
        else:
            date_truncated_df = df
        data = date_truncated_df[chart_type].array
        date = date_truncated_df.date.array
        plt.gcf().autofmt_xdate()
        ax.plot(date, data, label="{},{}".format(county, state))
    plt.grid(True)
    plt.legend()
    if "chart_title" in chart:
        chart_title = chart["chart_title"]
    else:
        chart_title = chart_type
    plt.title(f"{chart_title}")
    if "ylabel" in chart:
        plt.ylabel(chart["ylabel"])
    else:
        plt.ylabel(chart_type)
    plt.xlabel("Date")
    xtickrange = list(daterange[::3].array)
    last_date = pd.Timestamp(daterange.values[-1])
    if last_date not in xtickrange:
        xtickrange.append(last_date)
    plt.xticks(xtickrange, rotation=90)
    if "yscale" in chart:
        plt.yscale(chart['yscale'])

    plt.savefig(filename)
