from selenium import webdriver
import csv
import time
import datetime

driver = webdriver.Chrome()

covid_info = []


numdays=11
base = datetime.datetime.today()
date_list = [base - datetime.timedelta(days=x) for x in range(numdays)]
formatted_dates = [ date.strftime("%Y%m%d") for date in date_list]



for d in formatted_dates:
    driver.get("https://web.archive.org/web/{}/https://www.sccgov.org/sites/phd/DiseaseInformation/novel-coronavirus/Pages/home.aspx".format(d))
    dt = driver.find_element_by_class_name("ms-rteElement-H2")
    els = driver.find_elements_by_class_name("sccgov-responsive-table")
    if els:
        covid_data = els[0].text.split("\n")
        if len(covid_data) > 0:
            entry = {
                    'date': d,
                    'total_count': covid_data[6],
                    'hospitalized': covid_data[7],
                    'deaths': covid_data[8],
                    'international': covid_data[9],
                    'close_contact': covid_data[10],
                    'community_transmission': covid_data[11]
                }
            covid_info.append(entry)
            print(entry)
    time.sleep(2)

field_names = ["date", "total_count", "hospitalized", "deaths", "international", "close_contact", "community_transmission"]

with open('covid_data.csv.csv', 'w') as f:
    writer = csv.DictWriter(f, fieldnames = field_names)
    writer.writeheader()
    for row in covid_info:
        writer.writerow(row)

