# -*- coding: utf-8 -*-
"""
Created on Wed Nov 24 10:34:30 2021

@author: Fabian Maume. Tetriz.io
"""

#%%
import requests, json
import time
import pandas as pd

#Parrameters
Key = "Add you own key" 
Target_jobs = ["job title 1", "job title 2"]
Lead_list = "C:/Users/fabia/Downloads/QApop outreach 2 (1).xlsx"
Website_collum = "Website"
out_path = "C:\\Users\\fabia\\Dropbox\\QApopOutreach2.xlsx"
out_path_not_found = "C:\\Users\\fabia\\Dropbox\\LeadForPhantombuster.xlsx"
#Parrameters



#
data = pd.read_excel(Lead_list)
target = data[Website_collum]

#remove any duplicate
target = list(set(target))



def get_comapny_data(Key, domain):
    response = requests.get("https://api.apollo.io/v1/organizations/enrich?api_key="+ Key + "&domain=" + domain)
    result = response.json()
    try:
        result = result["organization"]
    except:
        print("no data for")
        print(domain)
    try:
        alexa_ranking = result["alexa_ranking"]
    except:
        alexa_ranking = "unknown"
    try:
        annual_revenue = result["annual_revenue"]
    except:
        annual_revenue = "unknown"
    try:
        country  = result["country"]
    except:
        country  = "unknown"
    try:
        estimated_num_employees  = result["estimated_num_employees"]
    except:
        estimated_num_employees  = "unknown"
    try:
        industry = result["industry"]
    except:
        industry = "unknown"
    try:
        keywords  = result["keywords"]
    except:
        keywords  = "unknown"
    try:
        Linkedin_uid = result["linkedin_uid"]
    except:
        Linkedin_uid ="unknown"
    
    return alexa_ranking, annual_revenue, country, estimated_num_employees, industry, keywords  , Linkedin_uid 

def getEmailEstension(email):
    start = email.index("@")
    result = email[start+1:len(email)]
    return result

def getDomaine(url):
    #short url to the part after http:// or https://
    start = url.index("//")
    result = url[start+2:len(url)]
    
    #remove / at the end of url
    if result[len(result)-1] == "/":
        result = result[0:len(result)-2]
    
    
    return result

def getEmployee(url, job):
        body =  {"api_key": Key,  "q_organization_domains": url, "page":1, "person_titles" : job}
        response = requests.post("https://api.apollo.io/v1/mixed_people/search", json = body)
        
        
        #response = requests.post("https://api.apollo.io/v1/mixed_people/search", data = {"api_key": Key,  "q_organization_domains": url, "page": 1, "person_titles" : ["organic", "SEO"]}, headers= { "Content-Type": "application/json", "Cache-Control": "no-cache"})
        result = response.json()
        return result
        
        s = requests.Session()
        s.headers.update({ "Content-Type: application/json"})
        



#
#########
#get list of employ

List_website = ""
Domain_list = list()

#create list of website
for url in target:
    List_website = List_website + "\n" + getDomaine(url)
    
    #create list of domain to check domain without leads later
    Domain_list.append(url)
    

List_website = List_website[1:len(List_website)]
People = list()
#Query first page
body =  {"api_key": Key,  "q_organization_domains": List_website, "page": 1, "person_titles" : Target_jobs}
response = requests.post("https://api.apollo.io/v1/mixed_people/search", json = body)
result = response.json()

[People.append(x) for x in result["people"]]
total_page = result["pagination"]["total_pages"]
page = 2

#get data from all the page
while ( page < total_page + 1):
    try:
        body =  {"api_key": Key,  "q_organization_domains": List_website, "page": page, "person_titles" : ["organic", "SEO"]}
        response = requests.post("https://api.apollo.io/v1/mixed_people/search", json = body)
        result = response.json()

        [People.append(x) for x in result["people"]]
        page = page + 1
    except:
        print("WARNING")
        print("run out of API calls")
        print("page:" + str(page))
        print("WARNING")
    
#Post process people
country = list()
first_name = list()
headline = list()
last_name = list()
linkedin_url = list()
oragnization = list()
title = list()


for element in People:
    try:
        stemp = element["country"]
    except:
        stemp = "unknwon"
    country.append(stemp)
    
    try:
        stemp = element["first_name"]
    except:
        stemp = "unknwon"
    first_name.append(stemp)
    try:
        stemp = element["last_name"]
    except:
        stemp = "unknwon"
    last_name.append(stemp)
    try:
        stemp = element["headline"]
    except:
        stemp = "unknwon"
    headline.append(stemp)
    try:
        stemp = element["linkedin_url"]
    except:
        stemp = "unknwon"
    linkedin_url.append(stemp)
    try:
        stemp = element["organization"]["website_url"]
    except:
        stemp = "unknwon"
    oragnization.append(stemp)
    try:
        stemp = element["title"]
    except:
        stemp = "unknwon"
    title.append(stemp)


export = pd.DataFrame({'country' :country ,'first_name' :first_name ,'headline' :headline ,'last_name' :last_name ,'linkedin_url' :linkedin_url ,'oragnization' :oragnization ,'title' :title , "detail": People})


 
writer = pd.ExcelWriter(out_path, engine='xlsxwriter',options={'strings_to_urls': False})                   
export.to_excel(writer,   header=True, index=False ) 
writer.close()   

#%%
#check list of company without url
Full_list = pd.DataFrame({"Domain": Domain_list})

#create list of found domain
found_url = list()
found = list()
for url in oragnization:
    stemp = getDomaine(url)
    found_url.append(stemp)
    found.append(True)
    

Result_list = pd.DataFrame({"Domain": found_url, "Found": found})

result = pd.merge(Full_list, Result_list, how = "left", on = "Domain")
result = result[result["Found"].isna()]

writer= pd.ExcelWriter(out_path_not_found, engine='xlsxwriter',options={'strings_to_urls': False})                   
result.to_excel(writer,   header=True, index=False ) 
writer.close()   
