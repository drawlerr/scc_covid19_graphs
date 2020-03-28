#!/usr/bin/env python3
import argparse
import csv
import datetime
import logging
import re
import sys

from selenium import webdriver
from selenium.common.exceptions import WebDriverException, TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By

DRIVERS = {
    "chrome": webdriver.Chrome,
    "safari": webdriver.Safari,
    "firefox": webdriver.Firefox
}


def get_driver(args, options=None):
    driver = DRIVERS[args.driver]
    if options is not None:
        return driver(options=options)
    return driver()


DEFAULT_OUTPUT_FILENAME = "covid_data.csv"


def get_arg_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument("--days-past",
                        type=int,
                        help="number of days of past data to fetch",
                        default='0')
    parser.add_argument("-o", "--output",
                        help="filename to output csv data",
                        default=DEFAULT_OUTPUT_FILENAME)
    parser.add_argument("-D", "--driver", choices=DRIVERS.keys(),
                        default="chrome", help="Select driver to use for crawl")
    parser.add_argument("--loglevel", dest="loglevel", choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        default="INFO", help="Set the logging level")
    return parser


CELLS_XPATH = "//div[@class='sccgov-responsive-table-cell']"
CELL_HEADER_REL_XPATH = "./div[@class='sccgov-responsive-table-cell-header']"
CELL_CONTENT_REL_XPATH = "./div[@class='sccgov-responsive-table-cell-content']"



def get_table_data(driver, url, timeout=1):
    data = {}
    driver.get(url)
    # they use an async JSON request for 1 row of data >_<
    logging.debug("Waiting for presence of table cells...")
    WebDriverWait(driver, timeout).until(ec.presence_of_element_located((By.XPATH, CELLS_XPATH)))
    logging.debug("Cells present!  Enumerating...")
    cells = driver.find_elements_by_xpath(CELLS_XPATH)
    for c in cells:
        header = c.find_element_by_xpath(CELL_HEADER_REL_XPATH).text
        if not header:
            # chrome + firefox fail to directly get header element text for some reason, so fall back to innerHTML
            # (safari .text works fine though, so leaving original call in place)
            header = c.find_element_by_xpath(CELL_HEADER_REL_XPATH).get_attribute("innerHTML")
            if not header:
                raise Exception("Failed to get header from table!")
        content = c.find_element_by_xpath(CELL_CONTENT_REL_XPATH).text
        data[header] = content
    return data


def get_ts_data(driver, xpath):
    data = []
    rects = driver.find_elements_by_xpath(xpath)
    labels = [r.get_attribute("aria-label") for r in rects]
    for lbl in labels:
        m = re.match(r"Date \w+, (\w+) (\d+), (\d{4}). ([\w ]+) (\d+).", lbl)
        if m:
            datestr = " ".join(m.groups()[0:3])
            date = datetime.datetime.strptime(datestr, "%B %d %Y")
            header = m.group(4)
            value = int(m.group(5))
            datum = {"Date": date,
                     header: value}
            logging.debug(datum)
            data.append(datum)
    return data


def get_dist_data(driver, xpath):
    data = []
    rects = driver.find_elements_by_xpath(xpath)
    labels = [r.get_attribute("aria-label") for r in rects]
    for lbl in labels:
        m = re.match(r"([\w -]+). %GT Count (\d.\d\d)%.", lbl)
        if m:
            header = m.group(1)
            perc = float(m.group(2))
            datum = {header: perc}
            logging.debug(datum)
            data.append(datum)
    return data


CASES_XPATH = "(//*[contains(@class, 'series')])[1]/*"
CASES_BY_AGE_XPATH = "(//*[contains(@class, 'series')])[2]/*"
DEATHS_BY_AGE_XPATH = "(//*[contains(@class, 'series')])[4]/*"
NEWCASES_XPATH = "(//*[contains(@class, 'series')])[5]/*"


def get_dashboard_data(driver, url):
    driver.get(url)
    logging.debug("Waiting for presence of table series rects...")
    WebDriverWait(driver, 30).until(ec.presence_of_element_located((By.XPATH, CASES_XPATH)))
    logging.debug("Cases present!  enumerating...")
    data = [get_ts_data(driver, CASES_XPATH),
            get_ts_data(driver, NEWCASES_XPATH),
            get_dist_data(driver, CASES_BY_AGE_XPATH),
            get_dist_data(driver, DEATHS_BY_AGE_XPATH),]
    return data


URL_SCC_NOVCOVID = "https://www.sccgov.org/sites/phd/DiseaseInformation/novel-coronavirus/Pages/home.aspx"
URL_SCC_NOVCOVID_DASH = "https://app.powerbigov.us/view?r=eyJrIjoiODI1YmRlMjUtODUwOC00ZDE0LWExMjMtMjA2ZDI2MTRlMGE4IiwidCI6IjBhYzMyMDJmLWMzZTktNGY1Ni04MzBkLTAxN2QwOWQxNmIzZiJ9"
WA_DATE_FORMAT = "%Y%m%d"
# maybe we can change this later if needed, but for now the webarchive date format is fine?
DATA_DATE_FORMAT = WA_DATE_FORMAT


def get_historical_data(driver, days_past):
    base = datetime.datetime.today()
    dates = [base - datetime.timedelta(days=x) for x in range(days_past)]
    data = []
    for d in dates:
        logging.info("Fetching data for %s", d.strftime(DATA_DATE_FORMAT))
        url = f"https://web.archive.org/web/{d.strftime(WA_DATE_FORMAT)}/{URL_SCC_NOVCOVID}"
        try:
            datum = get_table_data(driver, url)
        except TimeoutException:
            logging.warning("Timeout, moving on.")
            continue
        datum["Date"] = d.strftime(DATA_DATE_FORMAT)
        logging.debug("data row: %s", datum)
        data.append(datum)
    return data


COL_MAPPINGS = {
    "Total Cases": "Total Confirmed Cases",
    "Travel-Associated": "International Travel Associated",
    "Travel-related": "International Travel Associated",
    "Community Transmission": "Presumed Community Transmission",
    "New Cases Under Investigation": None,
    "Close Contact to Known Cases": None,
    "Recovered": None,
    "Positive": None
}


def transform_old_row(old_row, field_names):
    row = old_row.copy()
    # map new col names
    for k, v in COL_MAPPINGS.items():
        if k in row:
            old_val = row[k]
            del row[k]
            if v:
                row[v] = old_val
    # fill in missing cols
    delta = set(field_names) - row.keys()
    for d in delta:
        row[d] = ""
    return row


DATE_COL = "Date"


def write_data_to_csv(filename, data):
    logging.info("Writing %d rows of data to %s", len(data), filename)
    field_names = list(data[0].keys())
    # move date to front of line
    field_names.remove(DATE_COL)
    field_names = [DATE_COL] + field_names
    with open(filename, 'w') as f:
        writer = csv.DictWriter(f, fieldnames=field_names)
        writer.writeheader()
        for row in data:
            if row.keys() != set(field_names):
                logging.warning("Row %s has field names: row[%s] != field_names[%s]", row[DATE_COL],
                                row.keys(), set(field_names))
                row = transform_old_row(row, field_names)
            writer.writerow(row)


def dump_doc(driver, filename):
    """
     Dump current document source from driver to filename for debugging
    :param driver: selenium webdriver instancee
    :param filename: file to dump document contents to
    :return: None
    """
    doc = driver.page_source.encode('utf-8')
    with open(filename, "wb") as f:
        f.write(doc)


def main():
    parser = get_arg_parser()
    args = parser.parse_args()

    logging.basicConfig(level=getattr(logging, args.loglevel),
                        format='%(asctime)s %(name)s %(levelname)s %(message)s')
    # filter spammy logging
    if args.loglevel == "DEBUG":
        logging.getLogger("urllib3").setLevel(logging.INFO)
        logging.getLogger("selenium").setLevel(logging.INFO)

    logging.info("Booting webdriver...")
    driver = get_driver(args)
    try:
        if args.days_past > 0:
            logging.info("Getting %d days of historical data...", args.days_past)
            data = get_historical_data(driver, args.days_past)
        else:
            logging.info("Getting latest data...")
            data = get_dashboard_data(driver, URL_SCC_NOVCOVID_DASH)
    except WebDriverException:
        dump_doc(driver, "final.html")
        driver.save_screenshot("final.png")
        raise
    finally:
        driver.quit()

    logging.info("%d rows of data retrieved!", len(data))
    if len(data) > 0:
        # write_data_to_csv(args.output, data)
        return 0
    return 1


if __name__ == '__main__':
    sys.exit(main())
