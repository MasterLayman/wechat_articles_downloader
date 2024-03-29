# coding: utf-8

import json
import os
import re
import time

import requests
from bs4 import BeautifulSoup as bs, BeautifulSoup
from wechatarticles import LogUtil

class Url2Html(object):
    """根据微信文章链接下载为本地HTML文件"""

    def __init__(self, ext=0):
        """
        Parameters
        ----------
        ext: str
            预留参数
        """
        # 初始化日志
        self.logging = LogUtil()
        # self.data_src_re = re.compile(r'data-src="(.*?)"')
        # self.data_croporisrc_re = re.compile(r'data-croporisrc="(.*?)"')
        # self.src_re = re.compile(r'src="(.*?)"')

    @staticmethod
    def replace_name(title):
        """
        对进行标题替换，确保标题符合windows的命名规则

        Parameters
        ----------
        title: str
            文章标题

        Returns
        ----------
        str: 替换后的文章标题
        """
        rstr = r"[\/\\\:\*\?\"\<\>\|]"  # '/ \ : * ? " < > |'
        title = re.sub(rstr, "", title).replace("|", "").replace("\n", "").strip()
        return title

    @staticmethod
    def article_info(html):
        """
        根据提供的html源码提取文章中的公众号和作者

        Parameters
        ----------
        html: str
            文章HTML源码

        Returns
        ----------
        str: 公众号名字
        """
        soup = bs(html, "lxml")
        account = soup.find('a', {'id': 'js_name'}).text.strip()
        return account

    @staticmethod
    def get_timestamp(html):
        """
        根据提供的html源码提取文章发表的时间戳

        Parameters
        ----------
        html: str
            文章HTML源码

        Returns
        ----------
        int: 文章发表的时间戳
        """
        # var ct = "1683775847"
        timestamp = int(html.split('ct = "')[1].split('";')[0].strip())
        return timestamp

    @staticmethod
    def timestamp2date(timestamp):
        """
        时间戳转日期

        Parameters
        ----------
        timestamp: int
                时间戳

        Returns
        ----------
        str: 文章发表的日期，yyyy-mm-dd
        """
        ymd = time.localtime(timestamp)
        date = "{}-{}-{}".format(ymd.tm_year, ymd.tm_mon, ymd.tm_mday)
        return date

    def rename_title(self, title, html):
        soup = bs(html, "lxml")
        # 自动获取文章标题
        if title == None:
            title = soup.find('h1', {'id': 'activity-name'}).text.strip()
        if title == "":
            return "无标题"+str(uuid.uuid4()).replace("-","")
        title = self.replace_name(title)

        if self.account == None:
            try:
                account_name = self.article_info(html)
            except Exception as e:
                account_name = "未分类"
            self.account = account_name
        else:
            account_name = self.account
        try:
            date = self.timestamp2date(self.get_timestamp(html))
        except:
            date = ""
        # try:
        if not os.path.isdir(account_name):
            os.mkdir(account_name)
        # except:
        #     account_name = '未分类'
        #     if not os.path.isdir(account_name):
        #         os.mkdir(account_name)

        title = os.path.join(account_name, "[{}]-{}-{}".format(account_name, date, title))
        return title

    def load_img(self, html, path):
        """
        根据提供的html源码找出其中的图片链接，并对其进行替换

        Parameters
        ----------
        html: str
            文章HTML源码

        Returns
        ----------
        str: 替换html中在线图片链接为本地图片路径
        """
        data_croporisrc_lst = re.compile(r'data-croporisrc="(.*?)"').findall(html)
        data_src_lst = re.compile(r'data-src="(.*?)"').findall(html)
        src_lst = re.compile(r'src="(.*?)"').findall(html)

        img_url_lst = data_croporisrc_lst + data_src_lst + src_lst
        for img_url in img_url_lst:
            if "mmbiz.qpic.cn" in img_url:
                name = "{}.{}".format(img_url.split("/")[-2], img_url.split("/")[3].split("_")[-1])
                save_path = os.path.join(path, name)
                # 如果该图片已被下载，可以无需再下载，直接返回路径即可
                if not os.path.isfile(save_path):
                    response = self.session.get(img_url)
                    img = response.content
                    with open(save_path, "wb") as f:
                        f.write(img)
                # 以绝对路径的方式替换图片
                html = html.replace(img_url, os.path.join("imgs", name)).replace("data-src=", "src=")
        return html

    def load_css(self, html, path):
        """
        保存腾讯端css到本地并替换掉远端css

        Parameters
        ----------
        html: str
            文章HTML源码

        Returns
        ----------
        str: 替换html中在线css链接为本地css路径
        """
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup.find_all("link"):
            href = tag.get("href")
            type = tag.get("rel")
            if href.startswith("//res.wx.qq.com/mmbizappmsg/zh_CN/htmledition/js/assets/") and type[0]=="stylesheet":
                # 处理css地址
                css_url = "http:"+href
                # 获取css
                css_entity = self.session.get(css_url)
                # 获取css名字
                index = css_url.find("assets/")
                save_path = os.path.join(path, os.path.basename(css_url))
                # 下载为文件 存在就不下载了
                if not os.path.isfile(save_path):
                    with open(save_path, 'wb') as f:
                        f.write(css_entity.content)
                # 替换href为本地文件位置
                tag['href'] = os.path.join("css", os.path.basename(css_url))
        return str(soup)

    def download_media(self, html, path, baseUrl):
        soup = bs(html, "lxml")
        #
        video_list = {}
        # video
        scripts = soup.find_all('script')
        for script in scripts:
            # 判断为空
            if script.string is None:
                continue
            # 如果script标签的内容中包含'videoPageInfos'字符串
            if 'videoPageInfos' in script.string:
                # 使用正则表达式匹配'videoPageInfos'后面的值
                pattern = r'var videoPageInfos = (\[.*?\]);'
                match = re.search(pattern, script.string, re.DOTALL)
                if match:
                    # 如果找到了匹配的结果，解析为json格式并输出
                    raw_json_str = match.group(1).replace(" || ''","").replace(" * 1 || 0","").replace("'", "\"").replace("\\x26amp;","&")
                    # 使用正则表达式将属性名用双引号包裹
                    raw_json_str = re.sub(r"(\w+):", r'"\1":', raw_json_str).replace("\"http\"","http")
                    # 处理多余逗号
                    raw_json_str = re.sub(r'}\s*,\s*\]', '}]', raw_json_str).replace("],","]")
                    # 处理对象中的视频url
                    raw_json_str = raw_json_str.replace(".replace(/^http(s?):/, location.protocol)","").replace("(","").replace(")","");
                    # 转化为python对象
                    video_infos = json.loads(raw_json_str)
                    # 解析video_infos
                    for video in video_infos:
                        video_sources = {}
                        video_id = video["video_id"]
                        mp_video_trans_info = video["mp_video_trans_info"]
                        for mp_video in mp_video_trans_info:
                            format_id = mp_video["format_id"]
                            url = mp_video["url"]
                            video_sources[format_id] = url # +"&vid="+video_id+"&format_id="+format_id+"&support_redirect=0&mmversion=false"
                        video_list[video_id] = video_sources
                    # 匹配到script标签结束后退出循环
                    break
        # 遍历下载所有视频
        for video_id,video_sources in video_list.items():
            # 遍历该视频所有视频源
            for format_id,src in video_sources.items():
                # TODO 目前先写死下载10002的视频
                if "10002" in format_id:
                    # 声明下载地址
                    save_path = os.path.join(path, "videos", video_id+'.mp4')
                    # 存在文件则不下载
                    if os.path.isfile(save_path):
                        continue
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
                    response = self.session.get(src, timeout=(10, 1800), headers=headers)
                    # 将视频文件的二进制数据写入本地文件
                    with open(save_path, 'wb') as f:
                        f.write(response.content)

        # sounds
        mpvoices = soup.find_all("mpvoice")
        base_url = "https://res.wx.qq.com/voice/getvoice?mediaid="
        for mpvoice in mpvoices:
            # 声明下载地址
            save_path = os.path.join(path, "sounds", mpvoice["voice_encode_fileid"]+'.mp3')
            # 存在文件就不下载了
            if os.path.isfile(save_path):
                continue
            doc = self.session.get(base_url + mpvoice["voice_encode_fileid"])
            # 将视频文件的二进制数据写入本地文件
            with open(save_path, "wb") as f:
                f.write(doc.content)
            # 将mpvoice标签替换为自定义播放标签（仿）
            span_1 = soup.new_tag('span', attrs={'class': 'js_audio_frame db pages_reset audio_area'})
            span_2 = soup.new_tag('span', attrs={'class': 'wx_tap_card js_wx_tap_highlight appmsg_card_context db audio_card'})
            span_3 = soup.new_tag('span', attrs={'class': 'audio_card_bd'})
            sound_name = soup.new_tag('strong', attrs={'class': 'audio_card_title'})
            sound_name.string = mpvoice['name']
            audio_tag = soup.new_tag('audio', attrs={'controls': '', 'style': 'width:100%;padding-top:10px;'})
            source_tag = soup.new_tag('source', attrs={'src': f"sounds/{mpvoice['voice_encode_fileid']}.mp3", 'type': 'audio/mpeg'})
            audio_tag.append(source_tag)
            span_3.append(sound_name)
            span_3.append(audio_tag)
            span_2.append(span_3)
            span_1.append(span_2)
            mpvoice.replace_with(span_1)
        # 把音频相关的class样式加进classWhiteList
        scripts = soup.find_all('script')
        for script in scripts:
            # 判断为空
            if script.string is None:
                continue
            # 如果script标签的内容中包含'{classWhiteList:['字符串 添加上"db","pages_reset","audio_area","audio_card","audio_card_bd","audio_card_title"
            if '{classWhiteList:[' in script.string:
                pattern = r'(classWhiteList:\[")\w+'
                add_white_list = 'classWhiteList:["db","pages_reset","audio_area","audio_card","audio_card_bd","audio_card_title'
                script.string = re.sub(pattern, add_white_list, script.string)

        # 转为html
        html = str(soup)
        # 嵌入视频
        html = html.replace('<span class="weui-primary-loading"><span class="weui-primary-loading__dot"></span></span>',
                            '<video controls="" width="100%" height="100%"><source src="videos/\'+vid+\'.mp4" type="video/mp4"></video>')
        return html

    @staticmethod
    def replace_img(html):
        return html.replace("data-src=", "src=").replace("wx_fmt=jpeg", "wx_fmt=web")

    def run(self, url, mode, **kwargs):
        """
        Parameters
        ----------
        url: str
             微信文章链接
        mode: int
            运行模式
            1: 保存html源码，下载图片且替换图片路径，并下载视频与音频
            2: 返回html源码，不下载图片，替换src和图片为web
        kwargs:
            account:    公众号名
            title:      文章名
            date:       日期
            proxyUrl:   代理网址
            proxyPort:  代理端口

        Returns
        ----------
        str: HTML源码或消息
        """
        # 创建一个会话对象
        self.session = requests.Session()
        # 处理代理
        if "proxyUrl" in kwargs.keys() and "proxyPort" in kwargs.keys():
            self.proxyUrl = kwargs["proxyUrl"]
            self.proxyPort = kwargs["proxyPort"]
            proxy = {
                'http': 'http://'+proxyUrl+':'+proxyPort,
                'https': 'http://'+proxyUrl+':'+proxyPort
            }
            self.session.proxies = proxy
        # 主方法
        if   mode == 2:
            return self.replace_img(self.session.get(url).text)
        elif mode == 1:
            # 先从入口函数的参数中获取公众号名称,文章名称和发布时间
            account = kwargs["account"] if "account" in kwargs.keys() else None
            title = kwargs["title"] if "title" in kwargs.keys() else None
            date = kwargs["date"] if "date" in kwargs.keys() else None
            # account存为全局变量
            self.account = account
            if self.account and title and date:
                title = os.path.join(self.account, "[{}]-{}-{}".format(self.account, date, self.replace_name(title)),)
                if os.path.isfile("{}.html".format(title)):
                    return 0
                html = self.session.get(url).text
            else:
                html = self.session.get(url).text
                title = self.rename_title(title, html)
            # 文章所有信息会下载到这个文件夹中
            base_artical_path = title
            # 新建图片路径
            if not os.path.isdir(os.path.join(base_artical_path, "imgs")):
                os.makedirs(os.path.join(base_artical_path, "imgs"))
            # 新建css路径
            if not os.path.isdir(os.path.join(base_artical_path, "css")):
                os.makedirs(os.path.join(base_artical_path, "css"))
            # 新建视频路径
            if not os.path.isdir(os.path.join(base_artical_path, "videos")):
                os.makedirs(os.path.join(base_artical_path, "videos"))
            # 新建音频路径
            if not os.path.isdir(os.path.join(base_artical_path, "sounds")):
                os.makedirs(os.path.join(base_artical_path, "sounds"))
            # 替换网页中的静态资源路径为本地路径
            html = self.load_css(html, os.path.join(base_artical_path, "css"))
            html = self.load_img(html, os.path.join(base_artical_path, "imgs"))
            # 下载音频视频
            media_download_flag = True
            try:
                html = self.download_media(html, base_artical_path, url)
            except Exception as e:
                media_download_flag = False
                self.logging.info('{}---->{}'.format(title, e))
            # 生成html文件
            save_path = os.path.join(base_artical_path, "文章.html")
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(html)
            if(media_download_flag):
                return 1
                # return "地址为：{} 的文章下载完成!".format(url)
            else:
                return 0
                # return "地址为：{} 的文章下载失败!".format(url)
        else:
            print("please input correct mode num")
            return 0
            # return "地址为：{} 的文章下载失败!".format(url)