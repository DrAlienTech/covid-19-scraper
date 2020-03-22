#from google.colab import auth
from lxml import html
import requests
import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import sys
import os
import PyPDF2
import argparse
import tempfile
import urllib.request
import re
import urllib3
from tqdm import tqdm
import time



options = Options()
options.add_argument("--headless")

driver = webdriver.Firefox(executable_path=os.getcwd()+"/geckodriver",options=options)

#Currently requires google auth
#auth.authenticate_user()

#import gspread
#from oauth2client.client import GoogleCredentials

#gc = gspread.authorize(GoogleCredentials.get_application_default())

#Name must match, if it is changed in the file it must be changed here as well
#worksheet = gc.open('Beer Virus Automation').sheet1

#xpaths = worksheet.col_values(3)
#urls = worksheet.col_values(2)

total = 0

#Alabama
url = urllib.request.urlopen("https://services7.arcgis.com/4RQmZZ0yaZkGR1zy/arcgis/rest/services/COV19_Public_Dashboard_ReadOnly/FeatureServer/0/query?f=json&where=CONFIRMED%20%3E%200&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&outStatistics=%5B%7B%22statisticType%22%3A%22sum%22%2C%22onStatisticField%22%3A%22CONFIRMED%22%2C%22outStatisticFieldName%22%3A%22value%22%7D%5D&cacheHint=true")
content = url.read()
jc = json.loads(content)
AL = jc['features'][0]['attributes']['value']
print(AL)
total += AL

#Alaska
url = "http://dhss.alaska.gov/dph/Epi/id/Pages/COVID-19/monitoring.aspx"
xpathh = '//*[@id="ctl00_PlaceHolderMain_PageContent__ControlWrapper_RichHtmlField"]/div[2]/table/tbody/tr[9]/td[3]/p/text()'

page = requests.get(url)
tree = html.fromstring(page.content)
cnt = tree.xpath(xpathh)

AK = cnt[0]
print(AK)
total += int(AK)

#Arizona
#lol no

#Arkansas
driver.get("https://www.healthy.arkansas.gov/programs-services/topics/novel-coronavirus")
AR = int(driver.find_element_by_xpath("/html/body/div[7]/div[1]/table[4]/tbody/tr[1]/td[2]/b").text.replace(',', ''))
total += AR
print(str(AR))

#California
driver.get("https://www.latimes.com/projects/california-coronavirus-cases-tracking-outbreak/")
CA = int(driver.find_element_by_xpath("/html/body/article/div[1]/section[2]/div[1]/div[1]/p[1]").text.replace(',', ''))
total += CA
print(str(CA))

#Colorado (blaze it)
#too fkin tired to figure out canvas in js

#Connecticut
#KILL ME IT'S A PDF
f = tempfile.TemporaryFile()
driver.get("http://portal.ct.gov/Coronavirus")
pdfurl = driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/main/section[2]/div/div[2]/p[4]/span/strong/a").get_attribute('href')

urllib3.disable_warnings()
urllib3.util.ssl_.DEFAULT_CIPHERS += 'HIGH:!DH:!aNULL'
try:
    urllib3.contrib.pyopenssl.DEFAULT_SSL_CIPHER_LIST += 'HIGH:!DH:!aNULL'
except AttributeError:
    # no pyopenssl support used / needed / available
    pass


resp = requests.get(pdfurl, stream=True, verify=False)

# read 1024 bytes every time 
buffer_size = 1024

# get the total file size
file_size = int(resp.headers.get("Content-Length", 0))

# progress bar, changing the unit to bytes instead of iteration (default by tqdm)
progress = tqdm(resp.iter_content(buffer_size), f"Downloading file", total=file_size, unit="B", unit_scale=True, unit_divisor=1024)

for data in progress:
        # write data read to the file
        f.write(data)
        # update the progress bar manually
        progress.update(len(data))

pdfReader = PyPDF2.PdfFileReader(f)
firstPage = pdfReader.getPage(0).extractText().replace(',', '')

#print(firstPage)

CT = int(re.findall(r'-?\d+\.?\d*', re.findall("total of \n\d+", firstPage)[0])[0])
print(str(CT))
total += CT

f.close()


#Delaware
#Rasmit's job


#Flordia (insert flordiaman joke)
driver.get("https://experience.arcgis.com/experience/96dd742462124fa0b38ddedb9b25e429/")

while len(driver.find_elements_by_xpath("/html/body/div/div/div[2]/div/div/div/margin-container/full-container/div[2]/margin-container/full-container/div/div/div/div[2]/svg/g[2]/svg/text")) == 0:
    time.sleep(.1)

FL = int(driver.find_element_by_xpath("/html/body/div/div/div[2]/div/div/div/margin-container/full-container/div[2]/margin-container/full-container/div/div/div/div[2]/svg/g[2]/svg/text").replace(",", ""))
print(FL)
total += FL

#Output Handling
#store = gc.open_by_url('https://docs.google.com/spreadsheets/d/19PpoExlTc7I4V-HpxvrqDGDrKuRND10Hm3hA_pJvnjw/edit?usp=sharing').sheet2
#total = store.range('F1:F52')
print("total: " + str(total))
#worksheet.update_cells(total)
