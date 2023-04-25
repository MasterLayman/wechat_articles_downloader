# coding: utf-8
import sys
from cx_Freeze import setup, Executable

# 指定要打包的文件
build_exe_options = {
    "packages": ["logging", "os", "datetime", "json", "re", "time", "threading", "requests", "bs4"],
    "excludes": ["test/","jsons/"],
    "include_files": ["images/"]
}

# 创建Executable对象
base = None
if sys.platform == "win32":
    base = "Win32GUI"

executable = [
    Executable(
        "ArticleDownloader.py",         # 入口文件
        base=base,                      # 应用程序类型
        targetName="dowdload.exe",      # 目标程序名称
        icon="images/icon_lg.ico"          # 应用程序图标
    )
]

# 构建可执行文件的配置
setup (
    name='wechat_downloader',
    version='1.0',
    description='wechat articles downloader',
    options={"build_exe": build_exe_options},
    executables=executable
)
