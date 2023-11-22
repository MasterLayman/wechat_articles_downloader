# coding: utf-8

import requests


class DownLoadMediaByRequest:
    def __init__(self, src, save_path, proxyUrl, proxyPort):
        # 模拟真实用户的请求头
        headers = {
            "Host": "mpvideo.qpic.cn",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0",
            "Accept": "video/webm,video/ogg,video/*;q=0.9,application/ogg;q=0.7,audio/*;q=0.6,*/*;q=0.5",
            "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "Referer": "https://mp.weixin.qq.com/",
            "Origin": "https://mp.weixin.qq.com",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "video",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "cross-site",
            "Accept-Encoding": "identity"
        }
        # 视频最多下30分钟
        response = requests.get(src, proxies=self.proxies, timeout=(10, 1800), headers=headers)
        # 将视频文件的二进制数据写入本地文件
        with open(save_path, 'wb') as f:
            f.write(response.content)
