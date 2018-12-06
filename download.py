# -*- coding: utf-8 -*-
"""
Created on Tue Sep 18 15:06:34 2018

@author: mrthl
"""
import pandas as pd
import pdfkit
#from glob import glob
import os


file_log = open("log/log_download.txt","w")
#driver = ''
def log(string,end="\n",level=0):
    tab = '\t'*level
    file_log.write(tab+string+end)
    print(tab+string,end=end)
    
# Download part

print("Download PDF")

df_out = pd.read_csv("result.csv")
#df_out = pd.read_csv("test.csv")
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
        if link == None:
            break
        date = filing_date[i]
        filename = path+"/"+date+".pdf"
        log(filename,level=2)
        pdfkit.from_url(link, filename)