from bs4 import BeautifulSoup
import requests
import time
import random
import os
import sys


class VideoDownloader:

    def __init__(self,url=None,on_progress=None):


        
        #初始化
        self.url = url
        self.soup = None
        self.links = None # list,所有選項
        self.title = None
        self.links = None 
        self.select_url =None  # 即將下載的URL
        self.on_progress = on_progress  #
        self.downloaded = 0 #計算以下載的位元組

        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Mobile Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7,ja-JP;q=0.6,ja;q=0.5',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            # 加上關鍵的 sec- 瀏覽器行為特徵，破解高級防火牆
            'sec-ch-ua': '"Chromium";v="148", "Google Chrome";v="148", "Not/A)Brand";v="99"',
            'sec-ch-ua-mobile': '?1',
            'sec-ch-ua-platform': '"Android"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
        })
        
        # 3. 破解防盜鏈：自動把目標網址設定為來源網頁
        # if self.url:
        #     self.session.headers.update({'Referer': self.url})


    def run(self):
        if not self.url:
            raise Exception('No URL')
        try:
            self._get_soup()
            self._get_title()
            self._get_download_links()
            self._select_high_quality()
            self._start_download()
        except Exception as e:
            print(f'Error:{e}')

    def run_cli(self):
        '''命令列模式'''
        self._get_soup()
        self._get_title()
        self._get_download_links()
        print(self.links)

    def _get_soup(self): 

        time.sleep(random.uniform(1, 2))  #隨機延遲
        res = self.session.get(self.url)

        # HTTPError
        res.raise_for_status() 

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
            

    # def _select_mode(self):
    #     '''轉換CLI 或 UI 模式，預設UI '''
    #     if self.UI_mode:
    #         self._select_high_quality()
    #     else:
    #         self._manual_select()
    # def _enter_page(self):
    #     '''for CLI,optional'''

    #     if self.url is None:
    #         pass
    #     else:
    #         pass

    # def _manual_select(self): 
    #     '''for CLI'''
    #     pass

    # def _display_download_information(self):
    #     '''遍歷可用畫質選項'''

    #     for i , item in enumerate(self.links):
    #         text = item.get_text(strip= True)
    #         print(f"{i+1}",text)


 

'''測試'''

if __name__ == '__main__':

    url = 'https://www.85po.com/v/27158/zi-fen-yong--2/'
    downloader = VideoDownloader(url)
    downloader.run_cli()
