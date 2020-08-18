#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
    自動將無效商品結果串接道google sheets 並且透過 data studio 視覺化

'''
import gspread
import time
import pandas as pd 
from oauth2client.service_account import ServiceAccountCredentials 
import datetime
from datetime import date

auth_json_path = './drive_key.json'
gss_scopes = ['https://spreadsheets.google.com/feeds']



def auth_gss_client(path, scopes):
    credentials = ServiceAccountCredentials.from_json_keyfile_name(path, scopes)
    return gspread.authorize(credentials)



'''
    modify the date column in google sheet
'''
def update_rate(row_i):
    
    x = datetime.datetime.now() 
    m = x.strftime("%m")
    d = x.strftime("%d")
    d_ = date.today() 
    date_=d_.strftime('%Y-%m-%d')
    
    data = []
    data.append(date_)
    df_6 = pd.read_csv(m+d+"_6_result.csv")
    df_12 = pd.read_csv(m+d+"_result.csv")
    
    for rate in df_6['出錯比例']:
        data.append(rate)
    for rate in df_12['出錯比例']:
        data.append(rate)
    
    
    sheet.insert_row(data, row_i)


def update_all(row_i):
    
    x = datetime.datetime.now() 
    m = x.strftime("%m")
    d = x.strftime("%d")
    date_ = date.today()
    date_=date_.strftime('%Y-%m-%d')
    
    data = []
    data.append(date_)
    df_6 = pd.read_csv(m+d+"_6_result.csv")
    df_12 = pd.read_csv(m+d+"_result.csv")
    
    for rate in df_6['前端出錯數量']:
        data.append(rate)
    for rate in df_12['前端出錯數量']:
        data.append(rate)
    
    
    sheet_2.insert_row(data, row_i)




if __name__=="__main__":
    
    
    gss_client = auth_gss_client(auth_json_path, gss_scopes)
    spreadsheet_key_path_rate = '1V3zZf3ypv0lirXHvaZsUp2vMHkrOU5BSIF4VT6ulBbM'
    spreadsheet_key_path_all = '1LP-ve59dKxKaRuMkqJCVKvn1xnLJBOKuVxabQrvYkO0'
    sheet = gss_client.open_by_key(spreadsheet_key_path_rate).sheet1
    sheet_2 = gss_client.open_by_key(spreadsheet_key_path_all).sheet1
    
    row_i = 2
    
    
    update_all(2)
       
    
    update_rate(2)
        
    