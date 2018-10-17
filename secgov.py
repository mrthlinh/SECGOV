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
def log(string,end="\n",level=0):
    tab = '\t'*level
    file_log.write(tab+string+end)
    print(tab+string,end=end)
        
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


    
def main():

    
    
    all_tmp = glob("incomplete/*.csv")
    tmp_name = "incomplete/"+str(len(all_tmp) + 1) +".csv"
    
    
    
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
        
#        if (cik > 2000):
#            generateError()
        
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
#                this_date = table.find_element_by_xpath(xpath)
                
                this_dates = table.find_elements_by_xpath(xpath)              
                
                if (len(this_dates) >= 2):
                    for k in range(len(this_dates)):
                        dup_date = this_dates[k]
                        text = dup_date.find_element_by_xpath("preceding-sibling::*").text
                        if text in ['10-K','10-K/A']:
                            this_date = this_dates[k]
                else:
                    this_date = this_dates[0]
                    
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
        
    log("Finally, we finish")
    return 1


 

if __name__ == "__main__":
    MAX_RETRY = 3
    i = 0
    status = 0
    while(1):
        try:
            log("Attempt: "+str(i+1))
            status = main()
        except Exception as e:
            i += 1
            log(str(e))
            if i == MAX_RETRY:
                log("Reach maximum attempt to retry")
                break
        if (status == 1):
            break
    # END
    file_log.close()  
        

