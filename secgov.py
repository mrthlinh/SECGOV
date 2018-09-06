# -*- coding: utf-8 -*-
"""
Created on Wed Sep  5 19:49:09 2018

@author: mrthl
"""

# Scrap web
from selenium import webdriver
import pandas as pd
import numpy as np

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC
#from selenium.webdriver.support.ui import Select
#from selenium.webdriver.firefox.options import Options
#from selenium.webdriver.common.action_chains import ActionChains
#from selenium.webdriver.common.keys import Keys
import os
#import shutil 
#from glob import glob
#import json
import datetime
import traceback
#import time

def makeURL(cik):
    return "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK="+str(cik)+"&type=10-K&dateb=&owner=exclude&count=40"

def format_date(row):
    row = str(row)
    year = row[:4]
    month = row[4:6]
    day = row[6:8]
    return year + "-" + month + "-" + day

def log(string,end="\n",level=0):
    tab = '\t'*level
    file_log.write(tab+string+end)
    print(tab+string,end=end)
    
file_log = open("log/log.txt","w")

#print("========================= Main Program ===================================")
log("Open Bot Browser")
log("Time: "+str(datetime.datetime.now()))
download_dir = os.getcwd()
fp = webdriver.FirefoxProfile()
fp.set_preference("browser.download.folderList",2)
fp.set_preference("browser.download.dir", download_dir)
fp.set_preference("browser.download.manager.showWhenStarting",False)
fp.set_preference("browser.helperApps.neverAsk.saveToDisk","application/pdf")
fp.set_preference("pdfjs.disabled", True)
#
driver = webdriver.Firefox(fp)
#driver.get(url)

# Reading inputs
log("Reading inputs")
data = pd.read_csv("Compustat.csv")

cik_list = data['CIK Number'].unique()
#date = data['Filing Date']

data['Filing Date'] = data['Filing Date'].apply(format_date)
data['Period End date'] = data['Period End date'].apply(format_date)

criteria = ["promotion", "resign", "resignation", "retire", "retirement", "has retired", "will retire"]
columns = criteria + [ "combination", "document link"]
records = []

# Iterate
log("Iteration")
for cik in cik_list:
       
    url = makeURL(cik)
    
    log("CIK: "+str(cik),level=1)
    log("URL: "+url,level=1)
    
    driver.get(url)
    date_list = data.loc[data['CIK Number'] == cik,'Filing Date'].values
    
    # Wait for the table is fully loaded
    log("Wait for the table is fully loaded: ",end='',level=2)
    try:
        table = WebDriverWait(driver, 120).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "tableFile2"))
        )
    except Exception as e:
        log("Failed")
        traceback.print_exc(file=file_log)
        exit()
    log("Done")
    
#    # Wait for the table is fully loaded
#    log("\tWait for the table is fully loaded: ",end='')
#    try:
#        table = WebDriverWait(driver, 120).until(
#            EC.element_to_be_clickable((By.CLASS_NAME, "tableFile2"))
#        )
#    except Exception as e:
#        log("Failed")
#        traceback.print_exc(file=file_log)
#        exit()
#    log("Done")
#    
#    filing_date = table.find_elements_by_css_selector('td:nth-child(4)')
#    filing_date_text = [element.text for element in filing_date]
        
    for date in date_list:
#        index = filing_date_text.index(date)
#        this_date = filing_date[index]
        log("Date: "+date,level=2)

        
        xpath = "//td[ text()='"+date+"']"
        this_date = table.find_element_by_xpath(xpath)
        
        this_date.find_element_by_xpath("preceding-sibling::*[2]/a[@id='documentsbutton']").click()
        
        # Wait for elements to display
        log("Wait for elements to display: ",end='',level=2)
        
        try:
            table = WebDriverWait(driver, 120).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "tableFile"))
            )
        except Exception as e:
            log("Failed")
            traceback.print_exc(file=file_log)
            exit()
        log("Done")
        
        # Find Type of documents
        doc_type = table.find_elements_by_xpath("//td[text()='10-K']")[-1]
        doc_type.find_element_by_xpath("preceding-sibling::*[1]/a").click()
        
        # Wait for the document fully loaded
        log("Wait for the document fully loaded: ",end='',level=2)
        try:
            body = WebDriverWait(driver, 120).until(
                EC.element_to_be_clickable((By.TAG_NAME, "body"))
            )
        except Exception as e:
            log("Failed")
            traceback.print_exc(file=file_log)
            exit() 
        log("Done")
        doc_url = driver.current_url 
        text_html = driver.page_source.lower()
        record = [text_html.count(word) for word in criteria]
        
        np_temp = np.array(record)
        combination = int((np_temp == 0).any())
        
        log("Word Count: "+str(record),level=2)
        
        record = record + [combination,doc_url]
        records.append(record)
        
        
        log("Back to main page",level=2)
        driver.get(url)
        
        log("Wait for the table is fully loaded: ",end='',level=2)
        try:
            table = WebDriverWait(driver, 120).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "tableFile2"))
            )
        except Exception as e:
            log("Failed")
            traceback.print_exc(file=file_log)
            exit()
        log("Done")
        
df_temp = pd.DataFrame.from_records(records,columns=columns)
df_out = pd.concat([data,df_temp],axis=1)
df_out.to_csv("result.csv",index=False,encoding='utf-8')
log("Export data")
file_log.close()        
    
