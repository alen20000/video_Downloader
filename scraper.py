from bs4 import BeautifulSoup
import requests
import time
import random
import os
import sys


class VideoDownloader:

    def __init__(self,url=None,on_progress=None):

        self.session = requests.Session()
        self.session.headers.update({
            'user-agent':'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Mobile Safari/537.36',"Referer":"www.google.com"
            })
        
        #初始化
        self.url = url
        self.soup = None
        self.links = None # list,所有選項
        self.title = None
        self.UI_mode = True  # 預設自動模式
        self.links = None 
        self.select_url =None  # 即將下載的URL
        self.on_progress = on_progress  #
        self.downloaded = 0 #計算以下載的位元組

        #run
        self.run()

    def run(self):
        try:
            self._get_soup()
            self._get_title()
            self._get_download_links()
            self._select_mode()
            self._start_download()
        except Exception as e:
            print(e)

    def _get_soup(self): 

        time.sleep(random.uniform(2, 4))  #隨機延遲
        res = self.session.get(self.url,timeout=30)
        
        if not res.ok:
            raise Exception
        
        self.soup = BeautifulSoup(res.text,'html.parser')

    def _get_title(self):

        tag = self.soup.find('h1', class_='title')

        if not tag:
            raise Exception('找不到標題')
        
        self.title = tag.text.strip()
        print(f"影片名稱:{self.title}")

    def _get_download_links(self):
        '''找所有影片載點'''

        self.links =self.soup.find_all('a', attrs={'data-attach-session':'PHPSESSID'})

    def _select_mode(self):
        '''轉換CLI 或 UI 模式，預設UI '''
        if self.UI_mode:
            self._select_high_quality()
        else:
            self._manual_select()

    def _select_high_quality(self):
        '''自動選最高畫質'''
        priority=['1080p','720p','480p']

        for quality in priority:
            for item in self.links:
                if quality in item.get_text(strip=True):
                    self.select_url = item.get('href')
                    return 
        self.select_url = self.links[0].get('href')  #沒有就保底

    def _start_download(self): 
        '''專職下載，多緒在UI觸發時調用'''
        time.sleep(random.uniform(2, 4))
        res =  self.session.get(self.select_url ,stream=True,timeout=30)

        if not res.ok:
            raise Exception(f'下載請求失敗：{res.status_code}')
    
        total = int(res.headers.get('content-length', 0))  # 檔案總大小
        os.makedirs('downloads', exist_ok=True)

        with open(f'downloads/{self.title}.mp4','wb') as f:
            try:
                for chunk in res.iter_content(chunk_size=1024*1024):  # 每次1MB
                    f.write(chunk)
                    self.downloaded += len(chunk)
                    percent = int(self.downloaded / total * 100)
                    if self.on_progress:
                        self.on_progress(percent, self.downloaded, total)
            except Exception as e:
                raise Exception (f'下載中斷:{e}')  #這裡raise 給run 的 except 去處理，比較統一 

    def _enter_page(self):
        '''for CLI,optional'''

        if self.url is None:
            pass
        else:
            pass

    def _manual_select(self): 
        '''for CLI'''
        pass

    def _display_download_information(self):
        '''遍歷可用畫質選項'''

        for i , item in enumerate(self.links):
            text = item.get_text(strip= True)
            print(f"{i+1}",text)


 

