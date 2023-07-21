import os
import datetime
import re
from sihong.Utils import subtitleUtil
from googletrans import Translator

# 文件存在校验
def file_exists_check(filePath):
    if os.path.exists(filePath):
        return True
    else:
        return False

def get_time():
    current_time = datetime.datetime.now()
    formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S: ")

    return formatted_time


# 格式话时间，精确到秒 %Y-%m-%d %H:%M:%S
def date_time():
    new_date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S ")
    return new_date_time

# 重命名
def remove_symbol(word):
    word = re.sub('([^\u4e00-\u9fa5\u0030-\u0039\u0041-\u007a])', '', word)
    return word

# 检查视频素材完整性如果没下载完，删除文件后重新下载
def check_file_download_completed(downloadfile, savedfile, type):
    completedfilesize = os.stat(savedfile).st_size
    downloadinfo = "已下载文件大小:" + str(
        subtitleUtil.pybyte(completedfilesize, 2)) + ",油管文件大小:" + str(
        subtitleUtil.pybyte(downloadfile.filesize, 2) + "。")
    if completedfilesize == downloadfile.filesize:
        print(type + "文件已经完整下载, " + downloadinfo)
        return True
    elif completedfilesize < downloadfile.filesize:
        print(type + "文件未完整下载，删除旧文件, " + downloadinfo )
        return False

# 创建文件夹
def file_path_check(save_path, file_path):
    dirs = save_path + file_path
    if not os.path.exists(dirs):
        print("新视频，正在创建新文件夹")
        os.makedirs(dirs)

def googleTrans(content, type):
    if type == '中文':
        type = 'zh-cn'
    elif type == '英文':
        type = 'en'
    translator = Translator(service_urls=['translate.google.com.au'])  # 使用中国区域的Google翻译服务
    translation = translator.translate(content, dest=type)# 英文:'en' 中文: 'zh-cn'
    chinese_text = translation.text
    return chinese_text
