#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 10 17:14:51 2020

@author: yu_hsuantseng
"""
import requests
from requests.exceptions import ConnectionError
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


headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'}


def scrap(df):
    x = datetime.datetime.now() 
    m = x.strftime("%m")
    d = x.strftime("%d")
    browser = webdriver.Chrome(executable_path="./chromedriver") 
    r_status = []
    category = []
    date_=[]
    e = 0
    for source,url in tqdm(zip(df['商家'],df['連結'])):
        date_.append(m+"/"+d)
        try:
            r = requests.get(url = url , headers=headers)
            soup = BeautifulSoup(r.content,'lxml')
    #2
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
                        r_status.append("停售")
                        e+=1
                except:
                    print("error")
                    r_status.append("error")
                    pass 
                        
                try:
                    if soup.find("ul",class_="b-breadcrumb shop-breadcrumbs"):
                        tag = soup.find("ul",class_="b-breadcrumb shop-breadcrumbs").find_all("span")
                        cate = ""
                        for t in tag:
                            cate+=t.string
                                #cate+=">"
                        category.append(cate)
                    else:
                        category.append("null")
                except:
                    category.append("error")
                
        
#9 - complete and validated
            elif source == "friDay購物":
                try:
                    if soup.find("button",class_="buy"):
                        r_status.append("銷售中")
                    elif soup.find("button",class_="discount"):
                        r_status.append("銷售中")
                    else:
                        r_status.append("停售")
                        
                except:
                    r_status.append("error")
                    
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
                    
                    browser.get(url)
                    time.sleep(1.5)
                    soup=BeautifulSoup(browser.page_source,"html.parser")
            
                    try:
                        if soup.find("div",class_="tb-btn-buy"):
                            r_status.append("銷售中")
                        elif soup.find("div",class_="tb-btn-buy tb-btn-sku"):
                            r_status.append("銷售中")
                        else:
                            r_status.append("停售")
                        
                    except:
                        r_status.append("error")
                except:
                    print("error in 70")
                    
                    
                    
#122 complete and validated
            elif source == "生活市集":
                try:
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
                    r_status.append("停售")
                    e+=1
                    
            if len(r_status) > len(category):
                category.append("null")
            else:
                pass
   
        except:
            r_status.append("error")
            print(url)
        
        
    df['合作商家商品狀態'] = r_status
    df['商品分類'] = category
    df['時間'] = date_
    browser.quit()
    
    return df

def main():
    try:
        file = m+d+"_6__result_2.csv"
        df = pd.read_csv(m+d+"_6_2.csv")
        data= scrap(df)
        data.to_csv(file,index=False)
        time.sleep(64800)
    except:
        time.sleep(1800)
        main()
        
        

if __name__== "__main__":
    
    time.sleep(7200) 
    #schedule.every().day.at("07:00:00").do(main)
    
    while True:
        
        x = datetime.datetime.now()
        m = x.strftime("%m")
        d = x.strftime("%d")
        file = m+d+"_6__result_2.csv"
        if path.exists(file):
            pass
        else:
            main()
        
        
       
        
       
        
        
# 2020 04 09 time cost: 6:05:04   
        
        