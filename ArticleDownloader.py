import threading
import tkinter as tk
from tkinter import ttk, messagebox

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
        self.style.theme_use('default')
        # 设置背景色
        self.style.configure('TLabel', background='#f2f2f2')
        self.style.configure('TFrame', background='#f2f2f2')
        # 设置输入框的外观
        # self.style.configure('TEntry', foreground='#333', fieldbackground='#fff', font=('Arial', 14))
        # 设置滚动条的外观
        self.style.configure('TScrollbar', background='#e0e0e0')
        # 设置列表外观
        self.style.configure("Treeview.Heading", background="#93DB70", font=("Arial", 14, 'bold'))

        # 创建界面
        self.frame_top = ttk.Frame(self.root)
        self.frame_top.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)
        # 输入框label
        self.label_input = ttk.Label(self.frame_top, text='文章地址:', font=('Arial', 14, 'bold'))
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
        self.log_view = ttk.Treeview(master=self.frame_bottom, columns=[0, 1], show="headings")
        self.log_view.pack(fill=tk.BOTH, expand=True, anchor=tk.N)
        self.log_view.heading(0, text='文章路径', anchor=tk.CENTER)
        self.log_view.heading(1, text='状态', anchor=tk.CENTER)
        self.log_view.column(column=0, width=620, anchor=tk.W, stretch=True)
        self.log_view.column(column=1, width=150, anchor=tk.E, stretch=True)
        self.log_view.bind("<Double-Button-1>", self.get_article_url)

        # 主循环
        self.root.mainloop()

    def download_article(self):
        """
        获取地址栏文章地址下载文章

        :return:
        """
        url = self.entry_input.get()  # 获取输入框中的内容
        if not url:
            # 文章地址不能为空
            return
        # 在log_view中插入数据
        item = self.log_view.insert("", tk.END, values=(url, "下载中"))
        # 获取下载类
        downloader = Url2Html()

        # 线程任务
        def download_thread():
            try:
                res = downloader.run(url, mode=1, proxyUrl="127.0.0.1", proxyPort="7890")
            except Exception:
                status = "下载失败"
            else:
                if res == 1:
                    status = "下载完成"
                else:
                    status = "下载失败"
            self.log_view.item(item, values=(url, status))

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

    @staticmethod
    def get_article_url(event):
        """
        双击列表行数据复制文章地址

        :param event:
        :return:
        """
        selected_item = event.widget.selection()[0]
        values = event.widget.item(selected_item)['values']
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardText(values[1])
        win32clipboard.CloseClipboard()
        messagebox.showinfo(title="提示", message="复制成功。")

    @staticmethod
    def clipboard_get():
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
