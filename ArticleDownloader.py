import threading
import tkinter as tk
from tkinter import ttk

import win32clipboard

from wechatarticles import Url2Html


class ArticleDownloader:
    def __init__(self):
        # 创建窗口
        self.root = tk.Tk()
        # 窗口的标题
        self.root.title('微信文章下载工具')
        # 窗口默认大小
        self.root.geometry('800x500')
        # 设置图标
        self.root.iconbitmap('images/icon.ico')

        # 创建样式
        self.style = ttk.Style()
        # 设置背景色
        self.style.configure('TLabel', background='#f2f2f2')
        self.style.configure('TFrame', background='#f2f2f2')
        # 设置输入框的外观
        self.style.configure('TEntry', foreground='#333', fieldbackground='#fff', font=('Arial', 14))
        # 设置滚动条的外观
        self.style.configure('TScrollbar', background='#e0e0e0')

        # 创建界面
        self.frame_top = ttk.Frame(self.root)
        self.frame_top.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)
        # 输入框label
        self.label_input = ttk.Label(self.frame_top, text='文章地址:', font=('Arial', 14))
        self.label_input.pack(side=tk.LEFT)
        # 输入框（地址）
        self.entry_input = ttk.Entry(self.frame_top)
        self.entry_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))
        # 下载按钮
        self.btn_download = ttk.Button(self.frame_top, text='下载', command=self.download_article)
        self.btn_download.pack(side=tk.LEFT, padx=(10, 0))
        # 获取按钮
        self.btn_get = ttk.Button(self.frame_top, text='获取', command=self.get_article)
        self.btn_get.pack(side=tk.LEFT, padx=(10, 0))
        # 创建一个容器装载日志窗口
        self.frame_bottom = ttk.Frame(self.root)
        self.frame_bottom.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=10, pady=10)
        # 日志窗口
        self.log = tk.Text(self.frame_bottom, font=('Arial', 12), wrap='none', state='disabled')
        self.log.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        # 滚动条相关设置
        # 滚动条的滚动事件应该与文本框的垂直滚动联系起来。
        # self.scrollbar = ttk.Scrollbar(self.frame_bottom, command=self.log.yview)
        # 文本框的滚动应该与滚动条的位置联系起来。
        # self.log.configure(yscrollcommand=self.scrollbar.set)
        # 将滚动条放置在文本框的右侧，并设置它在垂直方向上填充整个可用空间。
        # self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 主循环
        self.root.mainloop()

    def download_article(self):
        """
        获取地址栏文章地址，并下载文章

        :return:
        """
        url = self.entry_input.get()  # 获取输入框中的内容
        if not url:
            self.log_configure_and_insert('文章地址不能为空')
            return
        self.log_configure_and_insert('开始下载文章，地址：' + url)
        downloader = Url2Html()

        # 线程任务
        def download_thread():
            res = downloader.run(url, mode=1)
            self.log_configure_and_insert(res)
        # 创建新线程并启动
        t = threading.Thread(target=download_thread)
        t.start()

    def get_article(self):
        """
        获取剪贴板中以https://mp.weixin.qq.com开头的文章地址

        :return:
        """
        recent_txt = self.clipboard_get()
        if recent_txt.startswith("https://mp.weixin.qq.com"):
            self.entry_input.delete(0, tk.END)
            self.entry_input.insert(0, recent_txt)

    def log_configure_and_insert(self, log_text):
        """
        在日志窗口中输出日志信息

        :param log_text: 日志文本
        :return:
        """
        # 设置文本框的状态为可编辑状态 打印日志 再次设为不可编辑
        self.log.configure(state='normal')
        self.log.insert(tk.END, log_text + '\n')
        self.log.configure(state='disabled')

    def clipboard_get(self):
        """
        获取剪贴板数据

        :return: 剪贴板内容
        """
        win32clipboard.OpenClipboard()
        data = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
        win32clipboard.CloseClipboard()
        return data


if __name__ == '__main__':
    ArticleDownloader()
