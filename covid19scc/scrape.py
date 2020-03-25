#!/usr/bin/env python3
import argparse
import csv
import datetime
import logging
import sys

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
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
                        default="safari", help="Select driver to use for crawl")
    parser.add_argument("--loglevel", dest="loglevel", choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        default="INFO", help="Set the logging level")
    return parser


CELLS_XPATH = "//div[@class='sccgov-responsive-table-cell']"
CELL_HEADER_REL_XPATH = "./div[@class='sccgov-responsive-table-cell-header']"
CELL_CONTENT_REL_XPATH = "./div[@class='sccgov-responsive-table-cell-content']"
TABLE_DATA_TIMEOUT = 1


def get_table_data(driver, url):
    data = {}
    driver.get(url)
    # they use an async JSON request for 1 row of data >_<
    logging.debug("Waiting for presence of table cells...")
    WebDriverWait(driver, TABLE_DATA_TIMEOUT).until(ec.presence_of_element_located((By.XPATH, CELLS_XPATH)))
    logging.debug("Cells present!  Enumerating...")
    cells = driver.find_elements_by_xpath(CELLS_XPATH)
    for c in cells:
        header = c.find_element_by_xpath(CELL_HEADER_REL_XPATH).text
        content = c.find_element_by_xpath(CELL_CONTENT_REL_XPATH).text
        data[header] = content
    return data


URL_SCC_NOVCOVID = "https://www.sccgov.org/sites/phd/DiseaseInformation/novel-coronavirus/Pages/home.aspx"
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
        datum = get_table_data(driver, url)
        datum["Date"] = d.strftime(DATA_DATE_FORMAT)
        logging.debug("data row: %s", datum)
        data.append(datum)
    return data


def write_data_to_csv(filename, data):
    logging.info("Writing %d rows of data to %s", len(data), filename)
    field_names = list(data[0].keys())
    # move date to front of line
    field_names.remove("Date")
    field_names = ["Date"] + field_names
    with open(filename, 'w') as f:
        writer = csv.DictWriter(f, fieldnames=field_names)
        writer.writeheader()
        for row in data:
            writer.writerow(row)


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
            data = [get_table_data(driver, URL_SCC_NOVCOVID)]
            d = datetime.datetime.today()
            data[0]["Date"] = d.strftime(DATA_DATE_FORMAT)
    except WebDriverException:
        driver.save_screenshot("final.png")
        raise
    finally:
        driver.quit()

    logging.info("%d rows of data retrieved!", len(data))
    if len(data) > 0:
        write_data_to_csv(args.output, data)
        return 0
    return 1


if __name__ == '__main__':
    sys.exit(main())
