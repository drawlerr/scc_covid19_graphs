import collections
from typing import Dict, OrderedDict

from selenium import webdriver
import csv
from datetime import date

driver = webdriver.Chrome()

field_names = ["date", "total_count", "hospitalized", "deaths", "international", "close_contact",
               "community_transmission"]

covid_info = []

with open('covid_data.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        covid_info.append(row)

today = date.today()

driver.get("https://www.sccgov.org/sites/phd/DiseaseInformation/novel-coronavirus/Pages/home.aspx")
dt = driver.find_element_by_class_name("ms-rteElement-H2")
els = driver.find_elements_by_class_name("sccgov-responsive-table")
if els:
    covid_data = els[0].text.split("\n")
    if len(covid_data) > 0:
        entry = collections.OrderedDict([
            ('date', today.strftime("%Y%m%d")),
            ('total_count', covid_data[6]),
            ('hospitalized', covid_data[7]),
            ('deaths', covid_data[8]),
            ('international', covid_data[9]),
            ('close_contact', covid_data[10]),
            ('community_transmission', covid_data[11]),
        ])
        covid_info.append(entry)
        print(entry)

with open('covid_data.csv', 'w') as f:
    writer = csv.DictWriter(f, fieldnames=field_names)
    writer.writeheader()
    for row in covid_info:
        writer.writerow(row)
