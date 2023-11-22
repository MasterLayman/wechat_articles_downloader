# coding: utf-8

import pycurl


class DownLoadMediaByCURL:
    def __init__(self, src, save_path, proxyUrl, proxyPort):
        with open(save_path, 'wb') as f:
            c = pycurl.Curl()
            # 设置请求的URL
            c.setopt(pycurl.URL, src)
            # 设置连接超时时间为 10 秒
            c.setopt(pycurl.CONNECTTIMEOUT, 10)
            # 设置代理
            c.setopt(pycurl.PROXY, "127.0.0.1")
            c.setopt(pycurl.PROXYPORT, 7890)
            # 模拟用户请求
            c.setopt(pycurl.REFERER, "https://mp.weixin.qq.com/");
            c.setopt(pycurl.USERAGENT, "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36");
            # 设置接收数据的超时时间为 1800 秒
            c.setopt(pycurl.TIMEOUT, 1800)
            # 将响应写入缓冲区
            c.setopt(pycurl.WRITEDATA, f)
            # 执行请求
            c.perform()
            # 获取响应状态码
            status_code = c.getinfo(c.RESPONSE_CODE)
            if status_code == 200:
                # 请求成功
                self.logging.info('视频请求成功！')
            else:
                # 请求失败
                self.logging.info('视频请求失败:'+status_code)
            c.close()