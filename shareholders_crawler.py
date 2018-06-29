import pandas as pd
import requests
import re
from selenium import webdriver
from selenium.webdriver.support.ui import Select
import time
from bs4 import BeautifulSoup as bs
import csv
import datetime
import dateutil.relativedelta
import os
import timeit

link = "https://warrants-hk.credit-suisse.com/en/underlying/hsi_e.cgi"
f = requests.get(link)
symbolslist0 = re.findall(r'<td.*?><a.*?>(\d+)(?=</a></td>)', f.text, re.MULTILINE)

symbolslist = symbolslist0[:50]

today = datetime.date.today()
startday = today - dateutil.relativedelta.relativedelta(months=12) + dateutil.relativedelta.relativedelta(days=1)

def get_shareholder():
    driver = webdriver.Chrome()
    url = 'http://www.hkexnews.hk/sdw/search/searchsdw.aspx'
    driver.get(url)

    for symbol in symbolslist:
        newpath = '{}_hist_sharehold'.format(symbol)
        if not os.path.exists(newpath):
            os.makedirs(newpath)
        date = startday
        if not os.path.exists("{}_hist_sharehold/{}_{}.csv".format(symbol,str(date),symbol)):
            while date != today:
                day = driver.find_element_by_name('ddlShareholdingDay')
                #select day
                selectDay = Select(driver.find_element_by_name('ddlShareholdingDay'))
                if date.day < 10:
                    selectDay.select_by_value('0'+str(date.day))
                else:
                    selectDay.select_by_value(str(date.day))
                #select month
                selectMon = Select(driver.find_element_by_name('ddlShareholdingMonth'))
                if date.month < 10:
                    selectMon.select_by_value('0'+str(date.month))
                else: 
                    selectMon.select_by_value(str(date.month))
                #select year
                selectYear = Select(driver.find_element_by_name('ddlShareholdingYear'))
                selectYear.select_by_value(str(date.year))
                #enter symbol code
                code = driver.find_element_by_name('txtStockCode')
                code.send_keys(symbol)
                #click search
                driver.find_element_by_name('btnSearch').click()

                shlist = driver.find_element_by_id('participantShareholdingList')
                soup = bs(shlist.get_attribute('innerHTML'), "lxml")
                rows = []

                for row in soup.find_all('tr'):
                    rows.append([val.text.strip() for val in row.find_all('td')])

                with open("{}_hist_sharehold/{}_{}.csv".format(symbol,str(date),symbol), "w") as output:
                    writer = csv.writer(output, lineterminator='\n')
                    writer.writerows(rows)

                
                date = date + dateutil.relativedelta.relativedelta(days=1)
                driver.back()

    driver.close()

if __name__ == '__main__':
    start = timeit.default_timer()
    get_shareholder()
    stop = timeit.default_timer()
    print('HIS share holding info download complete.\ntime cost:{}'.format((stop - start)))
    