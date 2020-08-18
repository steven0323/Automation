
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2020 07 29
@ project: automation check 
@ adding five shops to the existing project, making the converage rate to 80 %
@author: yu-hsuan tseng
@ 新增到17家前端商品狀態
"""
import requests
import os,sys
from bs4 import BeautifulSoup
import re
import time
import pandas as pd
import numpy as np
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from tqdm import tqdm
import matplotlib.pyplot as plt
from selenium.webdriver.chrome.options import Options
import smtplib
from email.mime.text import MIMEText
import mimetypes
from email.mime.multipart import MIMEMultipart
from email import encoders
from email.message import Message
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from tqdm import tqdm   
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import pandas as pd
from datetime import date,timedelta
import datetime
import os.path
from os import path



line_url = "https://buy.line.me"
headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'}
options = Options()
options.add_argument("user-data-dir={0}")
SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']
KEY_FILE_LOCATION = './client_secrets 2.json' 
VIEW_ID = '160738988'
sd = date.today() - timedelta(days=1)
sd=sd.strftime('%Y-%m-%d')
token = "KROeVpJKpfbcEQTa883Ep2G4w8jyDfB5ks5SnK6BhHM"

def initialize_analyticsreporting():
  """Initializes an Analytics Reporting API V4 service object.
  Returns:
    An authorized Analytics Reporting API V4 service object.
  """
  credentials = Credentials.from_service_account_file(KEY_FILE_LOCATION, scopes=SCOPES)
  #service = build('sheets', 'v4', credentials=credentials)

  # Build the service object.
  analytics = build('analyticsreporting', 'v4', credentials=credentials)

  return analytics

def get_report(analytics):
    
    return analytics.reports().batchGet(
      body={
        'reportRequests':[
        {
          'viewId': VIEW_ID,
          'pageSize': 30000,
          'dateRanges': [{'startDate': sd, 'endDate': sd}],
          'metrics': [{'expression': 'ga:totalEvents'}],
          'dimensions': [{'name': 'ga:dimension4'},{'name': 'ga:dimension5'},{'name': 'ga:dimension7'}],
           'dimensionFilterClauses': [{"filters": [{'dimensionName': "ga:dimension4",
                                          "operator": "IN_LIST",
                                          "expressions": ['23','42','48','910116','234']}]}],  
        }]  
      }
  ).execute()
    
   


def convert_to_dataframe(response):
    
  for report in response.get('reports', []):
    columnHeader = report.get('columnHeader', {})
    dimensionHeaders = columnHeader.get('dimensions', [])
    metricHeaders = [i.get('name',{}) for i in columnHeader.get('metricHeader', {}).get('metricHeaderEntries', [])]
    finalRows = []
    

    for row in report.get('data', {}).get('rows', []):
      dimensions = row.get('dimensions', [])
      metrics = row.get('metrics', [])[0].get('values', {})
      rowObject = {}

      for header, dimension in zip(dimensionHeaders, dimensions):
        rowObject[header] = dimension
        
        
      for metricHeader, metric in zip(metricHeaders, metrics):
        rowObject[metricHeader] = metric

      finalRows.append(rowObject)
      
      
  dataFrameFormat = pd.DataFrame(finalRows)    
  return dataFrameFormat

      
def print_response(response):
  """Parses and prints the Analytics Reporting API V4 response.
  Args:
    response: An Analytics Reporting API V4 response.
  """
  for report in response.get('reports', []):
      columnHeader = report.get('columnHeader', {})
      dimensionHeaders = columnHeader.get('dimensions', [])
      metricHeaders = columnHeader.get('metricHeader', {}).get('metricHeaderEntries', [])
      for row in report.get('data', {}).get('rows', []):
        dimensions = row.get('dimensions', [])
        dateRangeValues = row.get('metrics', [])
        for header, dimension in zip(dimensionHeaders, dimensions):
            print (header + ': ' + dimension)

        for i, values in enumerate(dateRangeValues):
            print('Date range: ' + str(i))
        for metricHeader, value in zip(metricHeaders, values.get('values')):
            print(metricHeader.get('name') + ': ' + value)


def ga():
    analytics = initialize_analyticsreporting()
    response = get_report(analytics)
  
    df = convert_to_dataframe(response)
    df = df.rename(columns={'ga:dimension4':'SID'})
    df = df.rename(columns={'ga:dimension5':'PID'})
    df = df.rename(columns={'ga:dimension7':'product status'})
    df = df.rename(columns={'ga:totalEvents':'事件總數'})
    df['SID'] = df['SID'].astype(int)
    
    
    return df


def send_csv(attachment):
    
    emailfrom = "Steph199603@gmail.com"
    emailto = "linetvltw@gmail.com"
    fileToSend = attachment
    username = "Steph199603@gmail.com"
    password = "yuhsuan0323"

    msg = MIMEMultipart()
    msg["From"] = emailfrom
    msg["To"] = emailto
    msg["Subject"] = "Daily update csv file"
    msg.preamble = "Daily update csv file"

    ctype, encoding = mimetypes.guess_type(fileToSend)
    if ctype is None or encoding is not None:
        ctype = "application/octet-stream"

    maintype, subtype = ctype.split("/", 1)

    if maintype == "text":
        fp = open(fileToSend)
    # Note: we should handle calculating the charset
        attachment = MIMEText(fp.read(), _subtype=subtype)
        fp.close()
    else:
        fp = open(fileToSend, "rb")
        attachment = MIMEBase(maintype, subtype)
        attachment.set_payload(fp.read())
        fp.close()
        encoders.encode_base64(attachment)
    attachment.add_header("Content-Disposition", "attachment", filename=fileToSend)
    msg.attach(attachment)

    server = smtplib.SMTP("smtp.gmail.com:587")
    server.starttls()
    server.login(username,password)
    server.sendmail(emailfrom, emailto, msg.as_string())
    server.quit()

    print("send csv successfully")
    
def send_mail(content):
    
    gmail_user = "Steph199603@gmail.com"
    gmail_pwd = "yuhsuan0323"
    
    msg = MIMEText(content)
    msg['Subject'] = '20200211 report'
    msg['From'] = gmail_user
    msg['To'] = 'Steph199603@gmail.com'
    
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.ehlo()
    server.login(gmail_user, gmail_pwd)
    server.send_message(msg)
    server.quit()

    print("Email has successfully sent to designated receiver") 
    
    

'''
    Sending daily result via line notigy 
'''


def lineNotifyMessage(token,msg):
    
    headers = {"Authorization":"Bearer "+token,
               "Content-Type":"application/x-www-form-urlencoded"}
    
    payload = {'message':msg}
    r = requests.post("https://notify-api.line.me/api/notify", headers = headers, params = payload)
    
    return r.status_code    
      

    
def api(sid,gid,browser):
    
    url = "https://buy-partner.line.me/manager/utility/product?shop="+str(sid)+"&gdid="+str(gid)
    browser.get(url)
    
    soup = BeautifulSoup(browser.page_source,'lxml')
    target = soup.find_all('td')
    
    if target != None:
        
        if target[2].text != None:
            link = target[2].text
        else:
            link ="null"
        if target[4].text != None:
            flag = target[4].text
        else:
            flag = "null"
    else:
        
        link = "null"
        flag = "null"
        
    return link,flag



'''
    2020 08 03 adding sid:23
'''

def scrap(df):
    x = datetime.datetime.now() 
    m = x.strftime("%m")
    d = x.strftime("%d")
    browser = webdriver.Chrome(executable_path="./chromedriver") 
    r_status = []
    category = []
    date_ = []
    e = 0
    i =0
    for source,url in tqdm(zip(df['商家'],df['連結'])):
        category.append("null")
        date_.append(m+"/"+d)
        try:
            
            i+=1
            r = requests.get(url = url , headers=headers)
            soup = BeautifulSoup(r.content,'lxml')
#42 -complete
            if source == "myfone購物":
                
                try:
                    if soup.find("button",class_="btn pay col-xs-6 openBtn"):
                        r_status.append("銷售中")
                    else:
                        r_status.append("停售")
                except:
                    r_status.append("error")
                    e+=1
                    pass
  

                    
#48 - complete
            elif source == "PChome 24h購物":
                url += "?ecid=1234567890123456789012345678901234567890123456789012345678901234"
                browser.get(url)
                soup = BeautifulSoup(browser.page_source,'lxml')
                try:
                    if soup.find("ul",class_="fieldset_box orignbutton"):
                        r_status.append("銷售中")
                    else:
                        r_status.append("停售")
                        
                    
                except:
                    r_status.append("error")
                    e+=1
                    pass
# 234 complete
            elif source == "屈臣氏Watsons":
                browser.get(url)
                soup = BeautifulSoup(browser.page_source,'lxml')
                try:
                    if soup.find("div",class_="buyBar").find_all("div",class_="ADD_TO_BAG btn-add-to-bag addtobag-pdp"):
                        r_status.append("銷售中")
                    else:
                        r_status.append("停售")
                except:
                    r_status.append("error")
                    e+=1
                    pass
 

#277 complete                   
            elif source == "蝦皮購物":
                browser.get(url)
                soup = BeautifulSoup(browser.page_source,'lxml')
                try:
                    if soup.find("button",class_="btn btn-solid-primary btn--l YtgjXY"):
                        r_status.append("銷售中")
                    else:
                        r_status.append("停售")
                except:
                    r_status.append("error")
                    e+=1
                    pass

#910116 -
            elif source == "燦坤線上購物":
                try:
                    if soup.find("div",class_="shpping"):
                        r_status.append("銷售中")
                    else:
                        r_status.append("停售")
                except:
                    r_status.append("error")


#910116 completed
            else:
                try:
                    if soup.find("button",class_="core-btn immediately-buy-btn cms-primaryBtnBgColor cms-primaryBtnTextColor cms-primaryBtnBorderColor"):
                        r_status.append("銷售中")
                    else:
                        r_status.append("停售")
                except:
                    r_status.append("error")
                
        except:
            print("scrapping function error: "+url)
            r_status.append("error")
            e+=1
            pass
    
    browser.quit()
    return r_status,category,date_ 



def dataframe(df,target):
    
    target_ = [23,42,48,910116,234]
    data = {'商家':[],'查詢總數':[],'前端出錯數量':[],'出錯比例':[]}
    for sid in target_:
        try:
            dt = df.loc[df['SID'].isin([sid])]
            all_ = target.loc[target['SID'].isin([sid])]
            data['商家'].append(get_partner(sid))
            data['查詢總數'].append(len(all_))
            data['前端出錯數量'].append(len(dt))
            data['出錯比例'].append(len(dt)/len(all_))
        except:
            print("dataframe error !!")
            print(sid)
    return data


def error_system(df):
    
    error = df.loc[df['合作商家商品狀態'].isin(['error'])]
    error.index = np.arange(1,len(error)+1)
    target_ = [23,42,48,910116,234]
    for sid in target_:
        try:
            sid_ = df.loc[df['SID'].isin([sid])]
            dt = error.loc[error['SID'].isin([sid])]
            if len(dt)/len(sid_) > 0.2:
                message = "合作商家 "+str(sid)+"無法解析比例高於 20% !!!"
                lineNotifyMessage(token,message)
        except:
            pass
            
        
def get_partner(num):
    
    if num == 42:
        return "myfone購物"
    elif num == 48:
        return "PChome 24h購物"
    elif num ==910116:
        return "康是美網購eShop"
    elif num == 234:
        return "屈臣氏Watsons"
    elif num ==23:
        return "燦坤線上購物"
    else:
        return "蝦皮購物"
                
def cookie(browser):
    #Store cookies
    cookies = browser.get_cookies()
    for cookie in cookies:
        with open('cookies.txt', 'a') as stored_cookies:
            stored_cookies.write(str(cookie) + '\n')
            

    #Restore cookies
    with open('cookies.txt') as stored_cookies:
        cookie = eval(stored_cookies.readline())
        browser.add_cookie(cookie)
                      
                
def main(df):
    
    try:
        
        options = Options()
        options.add_argument("user-data-dir={0}")
        browser = webdriver.Chrome(options=options,executable_path='./chromedriver')
        df = df
        source= []
        links= []
        flag = []
        num = 0
        #counting error target 記錄出錯位置
        num = 0
        # API GET LINKS
        for sid,gid in tqdm(zip(df['SID'],df['PID'])):
            try:
                num+=1
                lin,flag_ = api(sid,gid,browser)
                source.append(get_partner(sid))
                links.append(lin)
                flag.append(flag_)
            except:
                print("error occurs in for loop:",num)
                continue
        df['商家'] = source
        df['連結'] = links 
        df['API Flag'] = flag
        browser.quit() 
        return df  
    except:
        print("error occur in main function")
        browser.quit()
        time.sleep(1800)
        main()
        
      

    
    
if __name__== "__main__":

    #time.sleep(25200)
    count=0
    while True:
        
        x = datetime.datetime.now() 
        hr = x.strftime("%H")
        mini = x.strftime("%M")
        m = x.strftime("%m")
        d = x.strftime("%d")
        
        if hr == "12" and mini =="50":
            try:
                
                
                df = ga()
                df = df.sort_values(by='SID', ascending=True)
                df.index = np.arange(1,len(df)+1) 
                print(df.columns)
                target = df.loc[df['product status'].isin(['有貨'])]
                target.index = np.arange(1,len(target)+1) 
                
                data= main(target)
                data = data.loc[data['API Flag'].isin(['1'])]
                data.index = np.arange(1,len(data)+1)
               
                
                data.to_csv(m+d+"_19_layer1.csv")
            
                
                data = pd.read_csv(m+d+"_19_layer1.csv")
                
                
                result,category,date_= scrap(data) 
            
                data['合作商家商品狀態'] = result
                data['時間'] = date_
                data.to_csv(m+d+"_19_result_all.csv",index=False)
                print(" -------> Project complete")
            
                
                
            except:
                print()     
                print("system design error occur") 
                send_mail("df 3 system design error")
                time.sleep(54000)
        
        elif path.exists(m+d+"_19_result_all.csv"):
            
            if count ==0:
                count+=1 
                x = datetime.datetime.now() 
                hr = x.strftime("%H")
                mini = x.strftime("%M")
                send_mail("all three function has completed"+hr+mini)
                df = pd.read_csv(m+d+"_19_result_all.csv")
                error_system(df)
                error_ = df.loc[df['合作商家商品狀態'].isin(['停售'])]
                error_.index = np.arange(1,len(error_)+1)
                error_.to_csv(m+d+"_19_Data.csv",index=False)
            
                data = dataframe(error_,df)
                data = pd.DataFrame(data)
                data.to_csv(m+d+"_19_result.csv",index=False)
                  
                for sid,rate in zip(data['商家'],data['出錯比例']):
                    if float(rate) >= 0.05:
                    
                        message = "合作商家 "+str(sid)+"出錯比例高於5%"
                        lineNotifyMessage(token,message)
                    else:
                        pass
                
                send_csv(m+d+"_19_result_all.csv")
                send_csv(m+d+"_19_Data.csv")
            
                send_mail("Smile you dumbfuck !")
                time.sleep(64800)
            else:
                pass
            
        
        else:
            continue
        
   
