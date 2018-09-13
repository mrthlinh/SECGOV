# -*- coding: utf-8 -*-
"""
Created on Wed Sep  5 19:49:09 2018

@author: mrthl
"""

# Scrap web
from selenium import webdriver
import pandas as pd
import numpy as np
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC
import os
import datetime
import traceback
import pdfkit

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
#print("========================= Read list of words ===================================")
listofword = open("listofword.txt","r")
criteria = []
for line in listofword:
    criteria.append(line.split("\n")[0])
listofword.close()   

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
#data['Period End date'] = data['Period End date'].apply(format_date)

exact_match = ["exact "+word for word in criteria]
columns = exact_match + criteria + [ "combination", "document link"]
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
        
        # It is a 10-K/A document
        doc_type = table.find_elements_by_xpath("//td[text()='10-K/A']")
        if (len(doc_type) == 0):
            # Find Type of documents
            doc_type = table.find_elements_by_xpath("//td[text()='10-K']")
        
	
#        if (len(doc_type) == 0):
#            doc_type = table.find_elements_by_xpath("//td[text()='10-K/A']")
            
        doc_type[-1].find_element_by_xpath("preceding-sibling::*[1]/a").click()
        
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
        
        record_exact = [sum(1 for _ in re.finditer(r'\b%s\b' % re.escape(word), text_html)) for word in criteria]
        
        record_contain = [text_html.count(word) for word in criteria]
        
        np_temp = np.array(record_exact)
        combination = int((np_temp == 0).any())
        
        log("Word Count Exactly: "+str(record_exact),level=2)
        
        record = record_exact + record_contain + [combination,doc_url]
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
log("Export data to result.csv")

# Download part

log("Download PDF")

# list of companies
company_name = list(df_out['Company Name'].unique())

for company in company_name:
    path = "download/"+str(company)
    
    # Make new directory
    if not os.path.exists(path):
        os.makedirs(path)
    
    links = list(df_out[df_out['Company Name'] == company]["document link"])
    filing_date = df_out[df_out['Company Name'] == company]["Filing Date"]
    filing_date = [date.replace("-","") for date in filing_date]
    
    for i in range(len(links)):
        link = links[i]
        date = filing_date[i]
        filename = path+"/"+date+".pdf"
        log(filename,level=2)
        pdfkit.from_url(link, filename)

# END
file_log.close()        

