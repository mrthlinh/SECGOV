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

import json
from glob import glob
    
file_log = open("log/log.txt","w")
all_tmp = glob("incomplete/*.csv")
tmp_name = "incomplete/"+str(len(all_tmp) + 1) +".csv"

def save_checkpoint(cik,date,index):
    # Create a check point to result
    with open("log/error.json", 'w') as f:                    
        error_dict = {"CIK":str(cik), "date": str(date), "index":str(index)}
        json.dump(error_dict, f)
        
def generateError():
    return 1/0
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

index_resume = 0
log("Try to open resume file")
try:
    with open("log/error.json", 'r') as f:
        error_dict = json.load(f)
        CIK_resume = int(error_dict.get("CIK"))
        CIK_date = error_dict.get("date")   
        index_resume = int(error_dict.get("index"))
        log("CIK number: "+str(CIK_resume)+" - CIK date: "+CIK_date+"- index: "+str(index_resume))
except:
    CIK_resume = None
    CIK_date = None


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

cik_list = list(data['CIK Number'].unique())
#date = data['Filing Date']

data['Filing Date'] = data['Filing Date'].apply(format_date)
#data['Period End date'] = data['Period End date'].apply(format_date)

exact_match = ["exact "+word for word in criteria]
columns = exact_match + criteria + [ "combination", "document link"]
records = []

# Iterate
log("Iteration")
index_CIK_resume = 0
flag_resume = 1
if CIK_resume != None:
    index_CIK_resume = cik_list.index(CIK_resume)

#save_index = index_CIK_resume
for cik in cik_list[index_CIK_resume:]:
    
       
    url = makeURL(cik)
    
    log("CIK: "+str(cik),level=1)
    log("URL: "+url,level=1)
    
    driver.get(url)
    date_list = list(data.loc[data['CIK Number'] == cik,'Filing Date'].values)
    
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
    index_date_resume = 0
    
    
    if CIK_date != None:
        index_date_resume = date_list.index(CIK_date)
        flag_resume = 0
    CIK_date = None

        
    for date in date_list[index_date_resume:]:
#        index = filing_date_text.index(date)
#        this_date = filing_date[index]
        save_checkpoint(cik,date,index_resume)
        log("Index: "+str(index_resume)+" Date: "+date,level=2)

        try:
            xpath = "//td[ text()='"+date+"']"
            this_date = table.find_element_by_xpath(xpath)
            
            this_date.find_element_by_xpath("preceding-sibling::*[2]/a[@id='documentsbutton']").click()
        except Exception as e:
            traceback.print_exc(file=file_log)
            log("Error: Not find this date",level=1)
            record = [None for i in range(16)]
            records.append(record)
            index_resume += 1
            break
        
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
        
        record = [index_resume] + record_exact + record_contain + [combination,doc_url]
#        record =  record_exact + record_contain + [combination,doc_url]
        
        records.append(record)
        index_resume += 1
#        df_temp = pd.DataFrame.from_records(records,columns=columns)
        # save without header
        df_temp = pd.DataFrame.from_records(records)
        df_temp.to_csv(tmp_name,index=False,header=None,encoding='utf-8')
        
        
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
        
        

## Finally finish
#my_df = pd.DataFrame()
#for file in all_tmp:
#    tmp_file = pd.read_csv(file,header=None)
#    my_df = pd.concat([my_df,tmp_file],axis=1)
#
## Set index
#my_df = my_df.set_index(my_df.columns[0])
#my_df.columns = columns
##df_temp = pd.DataFrame.from_records(records,columns=columns)
#df_out = data.join(my_df,how='outer')
##df_out = pd.concat([data,df_temp],axis=1)
#df_out.to_csv("result.csv",index=False,encoding='utf-8')
#log("Export data to result.csv")
#
## Delete temp file
#log("Remove temporary files")
#all_temp = glob("incomplete/*.csv")
#for file in all_temp:
#    os.remove(file)
#
#
## Download part
#
#log("Download PDF")
#
## list of companies
#company_name = list(df_out['Company Name'].unique())
#
#for company in company_name:
#    path = "download/"+str(company)
#    
#    # Make new directory
#    if not os.path.exists(path):
#        os.makedirs(path)
#    
#    links = list(df_out[df_out['Company Name'] == company]["document link"])
#    filing_date = df_out[df_out['Company Name'] == company]["Filing Date"]
#    filing_date = [date.replace("-","") for date in filing_date]
#    
#    for i in range(len(links)):
#        link = links[i]
#        if link == None:
#            break
#        date = filing_date[i]
#        filename = path+"/"+date+".pdf"
#        log(filename,level=2)
#        pdfkit.from_url(link, filename)

# END
file_log.close()        

