# -*- coding: utf-8 -*-
"""
Created on Tue Sep 18 15:06:34 2018

@author: mrthl
"""
import pandas as pd
import pdfkit
from glob import glob
import os

def format_date(row):
    row = str(row)
    year = row[:4]
    month = row[4:6]
    day = row[6:8]
    return year + "-" + month + "-" + day

#print("========================= Read list of words ===================================")
listofword = open("listofword.txt","r")
criteria = []
for line in listofword:
    criteria.append(line.split("\n")[0])
listofword.close()  

exact_match = ["exact "+word for word in criteria]
columns = exact_match + criteria + [ "combination", "document link"]

data = pd.read_csv("Compustat.csv")

cik_list = list(data['CIK Number'].unique())
#date = data['Filing Date']

data['Filing Date'] = data['Filing Date'].apply(format_date)

all_tmp = glob("incomplete/*.csv")

# Finally finish
my_df = pd.DataFrame()
for file in all_tmp:
    tmp_file = pd.read_csv(file,header=None)
    my_df = pd.concat([my_df,tmp_file],axis=0)

# Set index
my_df = my_df.drop_duplicates()
my_df = my_df.set_index(my_df.columns[0])
my_df.columns = columns
#df_temp = pd.DataFrame.from_records(records,columns=columns)
df_out = data.join(my_df,how='outer')
#df_out = pd.concat([data,df_temp],axis=1)
df_out.to_csv("result.csv",index=False,encoding='utf-8')
print("Export data to result.csv")

# Delete temp file
all_temp = glob("incomplete/*.csv")
for file in all_temp:
    os.remove(file)


# Download part

print("Download PDF")

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
        print(filename,level=2)
        pdfkit.from_url(link, filename)