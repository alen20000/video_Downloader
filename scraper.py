from bs4 import BeautifulSoup
import requests
import time
import random
import os
import sys


class VideoDownloader:

    def __init__(self,url=None,on_progress=None):
        self.url = url
        self.headers={
            'user-agent':'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Mobile Safari/537.36'
            ,'Cookie':'_ga=GA1.1.1749939079.1758564712; kt_tcookie=1; kt_is_visited=1; _ga_3YMG8Q26HX=GS2.1.s1771777049$o15$g1$t1771778336$j60$l0$h0'
            }
        
        #初始化
        self.soup = None
        self.links = None # list,所有選項
        self.title = None
        self.auto_mode = True  # 預設自動模式
        self.links = None 
        self.select_url =None  # 即將下載的URL
        self.on_progress = on_progress  #
        self.downloaded = 0 #計算以下載的位元組

        #run
        self.run()

    def run(self):
        self._enter_page()
        self._get_soup()
        self._get_title()
        self._get_download_links()
        self._select_mode()
        self._start_download()

    def _enter_page(self):# 輸入目標網址

        if self.url is None:
            self.url = input('輸入網址:')
            self.headers['referer'] = self.url 
        else:
            self.headers['referer'] = self.url 

    def _get_soup(self): 
        time.sleep(random.uniform(2, 4))
        res = requests.get(self.url,headers=self.headers,timeout=30)
        self.soup = BeautifulSoup(res.text,'html.parser')

    def _select_mode(self):#選擇模式

        if self.auto_mode:
            self._select_high_quality()
        else:
            self._manual_select()

    def _select_high_quality(self):#順序模式、高到低
        priority=['1080p','720p','480p']

        for quality in priority:
            for item in self.links:
                if quality in item.get_text(strip=True):
                    self.select_url = item.get('href')
                    return self.select_url  # 第一個 return，找到就在這停了
        return  self.links[0].get('href') #沒找到保底
    
    def _manual_select(self): # 手動模式
        self._display_download_information()
        self._select_file()

    def _get_title(self):
        self.title = self.soup.find('h1', class_='title').text.strip()
        print(f"影片名稱:{self.title}")

    def _get_download_links(self):#抓所有下載點
        self.links =self.soup.find_all('a', attrs={'data-attach-session':'PHPSESSID'})
 

        
    def _display_download_information(self): # '''顯示選項'''

        for i , item in enumerate(self.links):
            text = item.get_text(strip= True)
            print(f"{i+1}",text)


    def _select_file(self): 
        '''手動，選擇下載檔案'''

        #輸入框，要減1
        choice = int(input('輸入要下載的檔案編號(int):')) -1
        select_item =  self.links[choice]
        self.select_url = select_item.get('href')
        print(f'下載目標網址:{self.select_url}')


    def _start_download(self): 
        '''下載'''
        time.sleep(random.uniform(2, 4))
        res = requests.get(self.select_url ,headers=self.headers,stream=True,timeout=30)
        total = int(res.headers.get('content-length', 0))  # 檔案總大小
        os.makedirs('downloads', exist_ok=True)

        with open(f'downloads/{self.title}.mp4','wb') as f:
            for chunk in res.iter_content(chunk_size=1024*1024):  # 每次1MB
                f.write(chunk)
                self.downloaded += len(chunk)
                percent = int(self.downloaded / total * 100)
                if self.on_progress:
                    self.on_progress(percent, self.downloaded, total)





