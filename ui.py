import tkinter as tk
from tkinter import ttk
import threading
import queue
from scraper import VideoDownloader
import sys

class TopFrame(tk.Frame):

    def __init__(self,parent):
        self.target_entries = []
        super().__init__(parent)
        self.pack(fill='x',padx=5,pady=5)
        self._build_input()

    def _build_input(self):

        for i in range(1,11):
            tk.Label(self, text=f"網址 No.{i}").grid(row=i, column=0, padx=5)
            entry = tk.Entry(self, width=45, fg='grey')
            entry.insert(0, "請輸入目標網址...")  # 加這行
            entry.grid(row=i, column=1, padx=5)

            #Bind event
            entry.bind("<FocusIn>", lambda e, en=entry: self._on_click(en))
            entry.bind("<FocusOut>", lambda e, en=entry: self._on_leave(en))
            self.target_entries.append(entry)

    def _on_click(self, entry):
        if entry.get() == "請輸入目標網址...":
            entry.delete(0, tk.END)  # 自動清除
            entry.config(fg='black')  # 字變黑色

    def _on_leave(self, entry):
        if entry.get() == "":
            entry.insert(0, "請輸入目標網址...")  # 空的就恢復提示
            entry.config(fg='grey')

    def get_urls(self):
        urls = []
        for e in self.target_entries:
            url = e.get()
            if url != "請輸入目標網址..." and url !="":
                urls.append(url)
        return urls
    

class MiddleFrame(tk.Frame):

    def __init__(self,parent):
        super().__init__(parent)
        self.pack(fill='both',expand=True)
        self._build()
        sys.stdout = self

    def _build(self):
        self.text =tk.Text(self,state='disabled')
        self.text.pack(fill='both',expand=True)


    def _insert(self, message):
        self.text.config(state='normal')  #unlock
        self.text.insert(tk.END, message)
        self.text.see(tk.END)
        self.text.config(state='disabled') #locked

    def write(self, message): #補 stdout的 write 要回補
        self.after(0, self._insert, message)

    def flush(self):           # 補上 stdout的 flush（不需要做事但要存在）
        pass


class BottonFrame(tk.Frame):

    def __init__(self,parent):
        super().__init__(parent)
        self.pack(fill='x', padx=5, pady=5)
        self._build_Button()
        self._build_progress()

    def _build_progress(self):
        self.progress =ttk.Progressbar(self, maximum=100 , length=300)
        self.progress.pack()

        self.progress_label = tk.Label(self, text="等待下載...")
        self.progress_label.pack()

    def _update_progress(self, percent, downloaded ,total):
        self.progress['value'] = percent
        self.progress_label['text']=f"{percent}%  |  {downloaded/1024/1024:.1f}MB / {total/1024/1024:.1f}MB"

    def _build_Button(self):
        self.urls = None
        ttk.Button(self, text="開始下載", command=self._on_download_click).pack() 

    def _on_download_click(self):
        '''按鈕被點擊'''
        threading.Thread(target=self._run_download, daemon=True).start()
        
    def _run_download(self):
        self.urls = self.master.top.get_urls()
        for i in self.urls:
            VideoDownloader(i,on_progress=self._update_progress)
            print('下載完成')

class App(tk.Tk): #繼承tk.Tk

    def __init__(self):
        super().__init__()
        self.title('85po下載器')
        self.top= TopFrame(self)
        self.console = MiddleFrame(self) #優先級要高，要先接管
        self.botton = BottonFrame(self)
        #啟動
        self.mainloop()