#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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
import schedule


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
          'pageSize': 40000,
          'dateRanges': [{'startDate': sd, 'endDate': sd}],
          'metrics': [{'expression': 'ga:totalEvents'}],
          'dimensions': [{'name': 'ga:dimension4'},{'name': 'ga:dimension5'},{'name': 'ga:dimension7'}],
          'dimensionFilterClauses': [{"filters": [{'dimensionName': "ga:dimension4",
                                          "operator": "IN_LIST",
                                          "expressions": ['2','18','20','50','90','9']}]}],  
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
    #time.sleep(30)
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



def scrap(df,browser):
    x = datetime.datetime.now() 
    m = x.strftime("%m")
    d = x.strftime("%d")
    e = 0
    r_status = []
    category = []
    date_ = []
    i=0
    for url,source in tqdm(zip(df['連結'],df['商家'])):
        date_.append(m+"/"+d)
        i+=1
        try:
            r = requests.get(url = url , headers=headers)
            soup = BeautifulSoup(r.content,'lxml')
            
#2 - complete and validated
            if source =="Yahoo奇摩超級商城":
        
        
                if soup.find("div",class_="warning"):
                    r_status.append("停售")
                    e+=1
                elif soup.find("button",class_="button button-default"):
                    r_status.append("銷售中")
                elif soup.find("button",class_="button button-disabled"):
                    r_status.append("停售")
                
                    e+=1
            
                elif soup.find("div",class_="challenge"):
                    r_status.append("需要登入驗證(18+)")
                
                elif soup.find("div",class_="hd header").text != None:
                    r_status.append("已沒有營業")
                    e+=1
                
                else:
                    r_status.append("error") 
                    pass
                try:
                    if soup.find("div",class_="bd"):
                        tag = soup.find("div",class_="bd").find_all("span")
                        cate = ""
                        for t in tag:
                            cate+=t.string
                            cate+=">"
                        category.append(cate)
                    else:
                        category.append("null")
                except:
                    category.append("error")
                    
      #3     -complete and validated  
            elif source =="Yahoo奇摩拍賣":
                
                try:
                    if soup.find("button",class_="buyNowButton__1aR87 actionButton__2aXKn button__yn_TD primaryButtonType2__m1h-8"):
                        r_status.append("銷售中")
                    elif soup.find("button",class_="buyNowButton__1aR87 actionButton__2aXKn button__yn_TD primaryButtonType2__m1h-8"):
                        
                        r_status.append("停售")
                    else:
                        r_status.append("停售")
                except:
                    r_status.append("error")
                try:
                    if soup.find("li",class_="pure-u breadcrumbListItem__2oVHs"):
                        cate=""
                        tags = soup.find("ul",class_="pure-g breadcrumbList__1Zra8").find_all("span")
                        for t in tags:
                            if t ==None:
                                pass
                            else:
                                cate+=t.string
                                cate+=">"
                        category.append(cate)
                    else:
                        category.append("Null")
                except:
                    category.append("Null")
 #1 - complete and validated                   
            elif source == "Yahoo奇摩購物中心":
                browser.get(url)
                time.sleep(0.5)
                soup=BeautifulSoup(browser.page_source,"html.parser")
                try:
                    if soup.find("div",class_="CheckoutButtons__buyNowBtn___1OZI0 CheckoutButtons__checkoutButton___kaatE"):
                        r_status.append("銷售中")
                    elif soup.find("div",class_="CheckoutButtons__disabledBtn___sWJo9 CheckoutButtons__checkoutButton___kaatE"):
                        r_status.append("停售")
                    else:
                        r_status.append("停售")
                except:
                    r_status.append("error")
                try:
                    if soup.find("ul",class_="CategoryBreadCrumb__breadCrumbList___1RZEp"):
                        cate=""
                        tags = soup.find("ul",class_="CategoryBreadCrumb__breadCrumbList___1RZEp").find_all("a")
                        for t in tags:
                            if t ==None:
                                pass
                            else:
                                cate+=t.string
                                cate+=">"
                        category.append(cate)
                    else:
                        category.append("Null")
                except:
                    category.append("Null")
                    
              
#18  -complete and validated   
            elif source == "台灣樂天市場":
                try:
                    if soup.find("button",class_="b-btn b-btn-type-a b-btn-large b-btn-emph b-btn-buynow itemcart add_to_cart qa-product-BuyNow-btn"):
                        r_status.append("銷售中")
       
           
                    elif soup.find("div",class_="age-restricted_footer"):
                        r_status.append("需要驗證登入 18+")
                   
                    elif soup.find("button",class_="b-btn b-btn-type-a b-btn-large b-btn-emph b-btn-buynow js-popover b-btn-deny b-disabled"):
                        r_status.append("停售")
                        e+=1
                    
                    elif soup.find("title").text == "錯誤 404 Not Found, 此網頁不存在 - Rakuten樂天市場":
                        r_status.append("停售")
                   
                        e+=1
                    else:
                        r_status.append("error")
                        e+=1
                        
                    try:
                        if soup.find("ul",class_="b-breadcrumb shop-breadcrumbs"):
                            tag = soup.find("ul",class_="b-breadcrumb shop-breadcrumbs").find_all("span")
                            cate = ""
                            for t in tag:
                                cate+=t.string
                                #cate+=""
                            category.append(cate)
                        else:
                            category.append("null")
                    except:
                        category.append("error")
                except:
                    print("error")
                    if len(category) !=i or len(r_status)!= i:
                        if len(category) < i:
                            category.append("error")
                        elif len(r_status) < i:
                            r_status.append("error")
                        else:
                            pass
                    else:
                        pass 
        
#9 - complete and validated
            elif source == "friDay購物":
                if soup.find("button",class_="buy"):
                    r_status.append("銷售中")
                elif soup.find("button",class_="discount"):
                    r_status.append("銷售中")
                else:
                    r_status.append("error")
                    e+=1
                try:
                    if soup.find("div",class_="path"):
                        tag = soup.find("div",class_="path").find_all("span")
                        cate = ""
                        for t in tag:
                            cate+=t.text
                            cate+=">"
                        category.append(cate)
                    else:
                        category.append("null")
                        
                except:
                    
                    category.appen("error")
                    
#20 -complete and validated
            elif source == "udn買東西":
        
                if  soup.find("a",class_="pd_buynow_short_btn"):
                    r_status.append("銷售中")
                else:
                    r_status.append("停售")
                    e+=1
                try:
                    if soup.find("ul",class_="crumb_list"):
                        tag = soup.find("ul",class_="crumb_list").find_all("a",class_="crumb_btn")
                        cate = ""
                        for t in tag:
                            cate+=t.find("span").string
                            cate+=">"
                        category.append(cate)
                    else:
                        category.append("null")
                except:
                    category.append("error")
                    
# 50 - complete and validated              
            elif source == "東森購物":
                try:
                    browser.get(url)
                    time.sleep(0.5)
                    soup=BeautifulSoup(browser.page_source,"html.parser")
                    try:
                        if browser.find_element_by_css_selector(".t-checkoutBtn.n-btn.n-btn--primary"):
                            r_status.append("銷售中")
                        else:
                            r_status.append("停售")
                            e+=1
                    except:
                        r_status.append("error")
                        
                    tag = soup.find_all("li",class_="n-breadcrumb__drop n-hover--drop")
                    if tag != None:
                        cate = ""
                        for t in tag:
                            cate+=t.find("span").string 
                            cate+=">"
                        category.append(cate)
                    else:
                        category.append("null")
                        pass
                   
                except:
                    print("error in for loop")
                    e+=1
                    
# 70  -complete and validated
                    
            elif source == "淘寶天貓":
                
                try:
                    
                    category.append("null")
                    browser.get(url)
                    time.sleep(0.5)
                    soup=BeautifulSoup(browser.page_source,"html.parser")
                    if soup.find("div",class_="tb-btn-buy"):
                        r_status.append("銷售中")
                    elif soup.find("div",class_="tb-btn-buy tb-btn-sku"):
                        r_status.append("銷售中")
                    else:
                        r_status.append("停售")
                except:
                    r_status.append("error")
                    print("error in 70")
                    
                    
                
#122 - error
            elif source == "生活市集":
                try:
                    browser.get(url)
                    time.sleep(0.5)
                    soup=BeautifulSoup(browser.page_source,"html.parser")
                    if soup.find("button",class_="buy-btn bg-dark-red border-white white"):
                        r_status.append("銷售中")
                    elif soup.find("button",class_="buy-btn bg-soldout-grey border-white white"):
                        r_status.append("停售")
                    else:
                        r_status.append("停售")
                except:
                    r_status.append("error")
                    
                try:
                    if soup.find("div",class_="breadcrumbs dark-grey"):
                        tag = soup.find("div",class_="breadcrumbs dark-grey").find_all("a")
                        if tag != None:
                            cate = ""
                            for t in tag:
                                cate+=t.string 
                                cate+=">"
                            category.append(cate)
                    else:
                        category.append("null")
                        pass
                except:
                    category.append("null")
                    
           
# 271 
            elif source == "小三美日":
                try:
                    if soup.find("a",class_="buy r-arrow add-cart"):
                        r_status.append("銷售中")
                    else:
                        r_status.append("停售")
                except:
                    r_status.append("error")
                try:
                    if soup.find("ul",class_="wrap-page breadcrumb"):
                        tags = soup.find("ul",class_="wrap-page breadcrumb").find_all("span")
                        cate =""
                        for t in tags:
                            
                            cate+=t.string
                            cate+=">"
                        category.append(cate)
                except:
                    category.append("null")
            
#286 -complete ,no category validated
            elif source == "家樂福線上購物":
                try:
                    category.append("null")
                    if soup.find("span",class_="hand-cursor empty-bg hidden-xs"):
                        r_status.append("銷售中")
                    else:
                        r_status.append("停售")
                except:
                    r_status.append("error")
        
            
#256 completed and validated          
            elif source == "松果購物":
                try:
                    if soup.find("div",class_="js-trigger-buy btn btn-buy btn-primary"):
                        r_status.append("銷售中")
                    else:
                        r_status.append("停售")
                    
                except:
                    r_status.append("error")
                try:
                    if soup.find_all("div",class_="breadcrumbs-set"):
                        tags = soup.find_all("div",class_="breadcrumbs-set")
                        cate =""
                        for t in tags:
                            tag = t.find_all("span")
                            for ta in tag:
                                cate+=ta.string
                                cate+=">"
                        category.append(cate)
                except:
                    category.append("null")
                    
# 90 complete and validated
            else:
                try:
                    browser.get(url)
                    time.sleep(0.5)
                    soup=BeautifulSoup(browser.page_source,"html.parser")
                    try:
                        if browser.find_element_by_css_selector(".t-checkoutBtn.n-btn.n-btn--primary"): 
                            r_status.append("銷售中")
                        else:
                            r_status.append("停售")
                            e+=1
                    except:
                        r_status.append("error")
                    try:
                        tag = soup.find_all("li",class_="n-breadcrumb__drop n-hover--drop")
                        if tag != None:
                            cate = ""
                            for t in tag:
                                for e in t.find("span"):
                                    cate+=e.string
                                    cate+=">"
                            category.append(cate)
                        else:
                            category.append("null")
                            pass
                    except:
                        category.append("error")
                    
                    
                except:
                    r_status.append("error")
                    e+=1
            if len(r_status) > len(category):
                category.append("null")
            else:
                pass
                
        except:
            print("error:",url)
            if len(r_status)<len(category):
                r_status.append("error")
            elif len(r_status)>len(category):
                category.append("error")
            elif len(r_status) <len(date_) and len(category)<len(date_):
                r_status.append("error")
                category.append("error")
            else:
                pass
            
    return r_status,category,date_



def error_system(df):
    
    error = df.loc[df['合作商家商品狀態'].isin(['error'])]
    error.index = np.arange(1,len(error)+1)
    target_ = [2,18,20,50,90,9]
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
    
    
    
    
    if num == 18:
        return "台灣樂天市場"
    elif num == 2:
        return "Yahoo奇摩超級商城"
    elif num == 1:
        return "Yahoo奇摩購物中心"
    elif num == 3:
        return "Yahoo奇摩拍賣"
    elif num == 256:
        return "松果購物"
    elif num == 70:
        return "淘寶天貓"
    elif num == 122:
        return "生活市集"
    elif num == 286:
        return "家樂福線上購物"
    elif num == 20:
        return "udn買東西" 
    elif num == 9:
        return "friDay購物"
    elif num == 50:
        return "東森購物"
    elif num == 271:
        return "小三美日"
    else:
        return "森森購物"
                
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
         
def dataframe(target,df):
    
    target_ = [2,18,20,50,90,9]
    data = {'商家':[],'查詢總數':[],'前端出錯數量':[],'出錯比例':[]}
    for sid in target_:
        try:
            dt = target.loc[target['SID'].isin([sid])]
            all_ = df.loc[df['SID'].isin([sid])]
            if len(dt)>1000:
                lineNotifyMessage(token,"合作商家:"+get_partner(sid)+" 無效商品超過1000品")
            data['商家'].append(get_partner(sid))
            data['查詢總數'].append(len(all_))
            data['前端出錯數量'].append(len(dt))
            data['出錯比例'].append(len(dt)/len(all_))
        except:
            print("dataframe error !!")
            print(sid)
    return data             
                
def main():
    
    try:
        
        df = ga()
        df = df.sort_values(by='SID', ascending=True)
        df.index = np.arange(1,len(df)+1) 
        df = df.loc[df['product status'].isin(['有貨'])]
        df.index = np.arange(1,len(df)+1) 
        options = Options()
        options.add_argument("user-data-dir={0}")
        browser = webdriver.Chrome(options=options,executable_path='./chromedriver')
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
        data = df.loc[df['API Flag'].isin(['1'])]
        data.index = np.arange(1,len(data)+1)
                
        data.to_csv(m+d+"_6layer1.csv")
        df_1 = data[:7000]
        df_1.index = np.arange(1,len(df_1)+1)
        df_1.to_csv(m+d+"_6_1.csv")
                
        df_2 = data[7000:13000]
        df_2.index = np.arange(1,len(df_2)+1)
        df_2.to_csv(m+d+"_6_2.csv")
                
                
        df_3 = data[13000:] 
        df_3.index = np.arange(1,len(df_3)+1)
        df_3.to_csv(m+d+"_6_3.csv")
                
        return df
    except:
        print("error occur in main function")
        browser.quit()
        pass
        

    
    
if __name__== "__main__":
    
    count = 0
    time.sleep(5400)
    while True:
        x = datetime.datetime.now() 
        m = x.strftime("%m")
        d = x.strftime("%d")
        hr = x.strftime("%H")
        mini = x.strftime("%M")
       
        if hr == "00" and mini =="01":
            
            try:
              
                main()
                df_3 = pd.read_csv(m+d+"_6_3.csv")
                browser = webdriver.Chrome(executable_path="./chromedriver")
                result,category,date_ = scrap(df_3,browser) 

                df_3['合作商家商品狀態'] = result
                df_3['商品分類'] = category
                df_3['時間'] = date_
                df_3.to_csv(m+d+"_6_result_3.csv",index=False)
                
                print(" -------> Project complete")
                pass
                
            except:
                print()     
                print("system design error occur") 
                send_mail("df 3 system design error")
                time.sleep(64800)
        
        elif path.exists(m+d+"_6__result_1.csv") and path.exists(m+d+"_6__result_2.csv") and path.exists(m+d+"_6_result_3.csv") and path.exists(m+d+"_6_all.csv")==False:
            
            if count ==0:
            
                hr = x.strftime("%H")
                mini = x.strftime("%M")
                send_mail("all three function has completed"+hr+mini)
                df_1 = pd.read_csv(m+d+"_6__result_1.csv")
                df_2 = pd.read_csv(m+d+"_6__result_2.csv")
                df_3 = pd.read_csv(m+d+"_6_result_3.csv")
                
                df = pd.concat([df_1,df_2])
                df = pd.concat([df,df_3])
                df.index = np.arange(1,len(df)+1)
                df = df.drop(['Unnamed: 0'],axis=1)
                df.to_csv(m+d+"_6_all.csv",index=False)
                send_csv(m+d+"_6_all.csv")
                error_system(df)
                
                notinstock = df.loc[df['合作商家商品狀態'].isin(['停售'])]
                notinstock.index = np.arange(1,len(notinstock)+1)
                notinstock.to_csv(m+d+"_6_Data.csv",index=False)
            
                data = dataframe(notinstock,df)
                data = pd.DataFrame(data)
                data.to_csv(m+d+"_6_result.csv",index=False)
                
                
                for sid,rate in zip(data['商家'],data['出錯比例']):
                    if float(rate) >= 0.05:
                    
                        message = "合作商家 "+str(sid)+"出錯比例高於5%"
                        lineNotifyMessage(token,message)
                    else:
                        pass
                
                 
                
                
                
                
                
                send_csv(m+d+"_6_result.csv")
                send_csv(m+d+"_6_Data.csv")
            
                send_mail("Smile you dumbfuck !")
                time.sleep(64800)
            else:
                pass
            
        
        else:
            continue
        
    











