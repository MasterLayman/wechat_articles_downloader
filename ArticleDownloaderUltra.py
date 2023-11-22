import threading

import ttkbootstrap as ttk
from ttkbootstrap.constants import *

import win32clipboard

from wechatarticles import Url2Html


class ArticleDownloaderUltra:
    def __init__(self):
        """
        窗口设置
        """
        # 日志行数
        self.log_row_num = 0;
        # 实例化创建应用程序窗口
        self.root = ttk.Window(
            title="微信文章下载工具",  # 设置窗口的标题
            themename="litera",  # 设置主题
            # iconphoto="images/icon.ico", # icon TODO 不明原因无效
            size=(800, 500),  # 窗口的大小
            position=(100, 100),  # 窗口所在的位置
            minsize=(0, 0),  # 窗口的最小宽高
            maxsize=(1920, 1080),  # 窗口的最大宽高
            resizable=None,  # 设置窗口是否可以更改大小
            alpha=1.0,  # 设置窗口的透明度(0.0完全透明）
        )
        # 创建界面
        self.frame_top = ttk.Labelframe(self.root, text="下载地址", padding=15)
        self.frame_top.pack(fill=X, expand=False, padx=10, anchor=N)
        # 创建一个容器装载日志窗口
        self.frame_bottom = ttk.Frame(self.root)
        self.frame_bottom.pack(fill=BOTH, expand=YES, padx=10, pady=10, anchor=S)
        # 输入框（地址）
        self.entry_input = ttk.Entry(self.frame_top)
        self.entry_input.pack(side=ttk.LEFT, fill=ttk.X, expand=True)
        # 下载按钮
        self.btn_download = ttk.Button(self.frame_top, text='下载', style='success', command=self.download_article).pack(side=ttk.LEFT, padx=(10, 0))
        # 获取按钮
        self.btn_get = ttk.Button(self.frame_top, text='获取', style='primary', command=self.get_article).pack(side=ttk.LEFT, padx=(10, 0))
        # 日志窗口
        self.log_view = ttk.Treeview(master=self.frame_bottom, bootstyle=INFO, columns=[0, 1, 2], show=HEADINGS)
        self.log_view.pack(fill=BOTH, expand=YES, anchor=N)
        # setup columns and use `scale_size` to adjust for resolution
        self.log_view.heading(0, text='序号', anchor=W)
        self.log_view.heading(1, text='文章路径', anchor=CENTER)
        self.log_view.heading(2, text='状态', anchor=E)
        self.log_view.column(column=0, anchor=W, width=int(self.log_view.winfo_width() * 0.1), stretch=True)
        self.log_view.column(column=1, anchor=CENTER, width=int(self.log_view.winfo_width() * 0.8), stretch=True)
        self.log_view.column(column=2, anchor=E, width=int(self.log_view.winfo_width() * 0.1), stretch=True)
        # 设置行和列的权重，让frame_top和frame_bottom占满整个窗口的Y轴空间
        self.root.columnconfigure(0, weight=1)
        # 主循环
        self.root.mainloop()

    def download_article(self):
        """
        获取地址栏文章地址，并下载文章

        :return:
        """
        url = self.entry_input.get()  # 获取输入框中的内容
        if not url:
            # 文章地址不能为空
            return
        # 获取行号
        self.log_row_num = self.log_row_num + 1
        # 在log_view中插入数据
        item = self.log_view.insert("", ttk.END, values=(self.log_row_num, url, "下载中"))
        # 获取下载类
        downloader = Url2Html()

        # 线程任务
        def download_thread():
            try:
                res = downloader.run(url, mode=1)
            except Exception as e:
                self.log_view.item(item, values=(self.log_row_num, url, "下载失败"))
            if res == 1:
                self.log_view.item(item, values=(self.log_row_num, url, "下载完成"))
            else:
                self.log_view.item(item, values=(self.log_row_num, url, "下载失败"))

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
            self.entry_input.delete(0, END)
            self.entry_input.insert(0, recent_txt)

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
    ArticleDownloaderUltra()
