# Automation
# 無效商品偵測
1. 須先下載 google chrome driver - version 83.0  Link:  https://chromedriver.chromium.org/downloads
2. 開通google gmail api 存取權限, google sheet api並取得token
3. 下載 Google Analytics client secret key - Json file
4. 在 main6 / main12/ main18 三隻程式碼裡面修改執行時間，設定完時間再另外修改剩下的四隻程式
5. 18家都爬完並產生完正確資料之後，再執行 write_to_sheet.py 
6. 檢查google sheet 是否完成更新
