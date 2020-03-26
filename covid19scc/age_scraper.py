from selenium import webdriver
import csv
import time
from datetime import date

driver = webdriver.Chrome()

field_names = ["date", "20_or_under", "21-30", "31-40", "41-50", "51-60", "61-70", "71-80", "over_80", "unknown_age"]

covid_info = []

# with open('covid_age_data.csv', 'r') as f:
#     reader = csv.DictReader(f)
#     for row in reader:
#         covid_info.append(row)

today = date.today()

driver.get("https://www.sccgov.org/sites/phd/DiseaseInformation/novel-coronavirus/Pages/home.aspx")
el = driver.find_element_by_id("WebPartWPQ2")
count = 0
age_info = el.text.split(" ")

entry = {
   'date': today.strftime("%Y%m%d"),
    '20_or_under': age_info[19].split('\n')[1],
    '21-30': age_info[20],
    '31-40': age_info[21],
    '41-50': age_info[22],
    '51-60': age_info[23],
    '61-70': age_info[24],
    '71-80': age_info[25],
    'over_80': age_info[26],
    'unknown_age': age_info[27].split('\n')[0]

}

covid_info.append(entry)
print(entry)


with open('covid_age_data.csv', 'w') as f:
    writer = csv.DictWriter(f, fieldnames = field_names)
    writer.writeheader()
    for row in covid_info:
        writer.writerow(row)