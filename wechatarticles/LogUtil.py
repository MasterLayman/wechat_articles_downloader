import logging
import os
from datetime import datetime


class LogUtil:
    def __init__(self, ext=1):
        # 创建控制台日志处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(console_formatter)
        #如果ext是1则开始本地日志记录
        file_handler = None
        if ext==1:
            log_dir = os.path.join("D:", "pythonlog", "wechat", datetime.today().strftime("%Y-%m-%d"))
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            # 创建文件日志处理器
            file_handler = logging.FileHandler(filename=os.path.join(log_dir, "app.log"), mode='a', encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(file_formatter)
        # 创建日志对象
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)  # 修改日志级别为DEBUG
        # 添加处理器
        self.logger.addHandler(console_handler)
        if file_handler:
            self.logger.addHandler(file_handler)

    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)
