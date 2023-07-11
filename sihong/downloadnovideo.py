# 获取以下内容并写入excel
# 作者/标题/浏览量/日期/描述/链接
from urllib.error import HTTPError, URLError
import self as self
import openpyxl as xl
from pytube import YouTube
from pytube.cli import on_progress
import time
import os
import requests
import re
import datetime
from pytube import Channel
import sys
from googletrans import Translator



import subtitleUtil

win_path = "/home"  # TODO
default_ptah = win_path + '/youtube/'  # excel默认保存露营 # TODO

def get_path():
    if sys.platform.startswith('win'):
        return 'D:\\'  # Windows系统路径
    elif sys.platform.startswith('darwin') or sys.platform.startswith('linux'):
        return '/Users/sihonghuang/Documents/'  # macOS和Linux系统路径
    else:
        return ''  # 其他操作系统路径（可以根据需求进行适当修改）



def downloadYoutube(url):
    yt = get_yt(url)
    fuchsia = '\033[38;2;255;00;255m'  # color as hex #FF00FF
    reset_color = '\033[39m'
    # 配置信息
    author = remove_symbol(yt.author)  # 视频作者（不带空格）
    title = remove_symbol(yt.title)  # 视频标题(不带空格)
    print("视频上传时间: " + yt.publish_date.strftime("%Y%m%d") + "\n" + "今天的日期: " + time.strftime("%Y%m%d"))
    save_path = save_path_check(channel_type(author))
    print("save_path:"+ save_path)
    file_path = author + "/" + yt.publish_date.strftime("%Y-%m-%d") + "_" + title
    print("file_path:"+ file_path)
    print(f'\n' + fuchsia + '开始下载: ', author + "----" + title, '~ viewed', yt.views, 'times.')
    # 下载前先检查是否有该路径，没有则创建
    file_path_check(save_path, file_path)
    start = time.time()
    # 下载字幕
    subtitle = download_subtitles(yt, save_path, file_path, title)
    # 下载封面
    video_img = request_download(yt.thumbnail_url, save_path, file_path, title)  # 下载视频封面
    # 下载音频
    audio = download_audio(yt, save_path, file_path)
    # 下载视频
    video_num = 0

    # 写入excel #转移到下载视频里
    write_to_excel(save_path, yt.author, yt.title, yt.views, yt.publish_date, yt.description, url)
    end = time.time()
    if video_img is True or video_num != 0 or audio is True:
        print(f'\n完成下载:  {title}' + "下载完成,共计花费了{:.2f}秒".format(end - start) + reset_color)
    else:
        print(f'\n====================本集视频素材均已下载====================')
    return video_num


"""
获取YouTube下载
"""
def get_yt(url):
    while True:
        try:
            yt = YouTube(url, on_progress_callback=on_progress)
            return yt
            break
        except HTTPError:
            self.logger.error("请求出错一次：HTTPError")
            continue
        except URLError:
            self.logger.error("请求出错一次：URLError")
            continue


"""
下载字幕
"""


def download_subtitles(yt, save_path, file_path, title):
    # print("开始下载字幕")
    num = 0
    print(yt.caption_tracks)
    caption_list = {'English': 'en', 'English (auto-generated)': 'a.en', 'Chinese': 'zh',
                    'Chinese (Simplified)': 'zh-Hans', 'Chinese (Taiwan)': 'zh-TW', 'Chinese (China)': 'zh-CN',
                    'English (United States)': 'en-US', 'English (United Kingdom)': 'en-GB'}  # 'English': 'en',
    for language in caption_list:
        for caption in yt.caption_tracks:
            if language == caption.name:
                print(language)
                caption_list_caption_name = caption_list[caption.name].replace(".", "")
                print(caption_list_caption_name)
                if file_exists_check(
                        save_path + file_path + "/" + caption_list_caption_name + title + " (" + caption_list[
                            language] + ").srt"):
                    # print(language + "字幕文件已下载，无需重新下载")
                    num += 1
                else:
                    yt.captions[caption_list[caption.name]].download(title=caption_list[caption.name] + title,
                                                                     output_path=save_path + file_path, srt=True)
                    # print(caption_list[caption.name] + title + " (" + caption_list[language] + ").srt")
                    print(language + "字幕下载完毕......")
            else:
                continue
    if num == 0:
        return True
    else:
        return False


# 下载视频
def download_video(yt, save_path, file_path):
    num = 0
    video_streams = yt.streams.filter(file_extension='mp4')  # 获取所有的视频流（筛选出文件扩展名为mp4的流）
    sorted_streams = sorted(video_streams, key=lambda stream: stream.filesize,reverse=True)  # 根据文件大小进行排序
    video = sorted_streams[0]
    #video = yt.streams.filter(adaptive=True).filter(mime_type='video/webm').first()  # 选择清晰度最高的视频
    video_name = 'Video_' + remove_symbol(video.default_filename.split(".")[0]) + '.'+video.default_filename.split(".")[-1]
    completedfilesize = save_path + file_path + "/" + video_name
    print("视频路径: " + save_path + file_path + "/" + video_name)

    if file_exists_check(save_path + file_path + "/" + video_name):
        result = check_file_download_completed(video, completedfilesize, '视频')
        if result is False:
            print("下载的文件与油管文件大小不符,重新下载")
            video.download(output_path=save_path + file_path, filename=video_name)
            num = 1
            return num
        else:
            return num
    else:
        string = subtitleUtil.pybyte(video.filesize, 2)
        print(date_time() + "未下载过,开始下载视频,视频大小 %s ......" % string)
        video.download(output_path=save_path + file_path, filename=video_name)
        # 写入excel
    # if excel_type == 1:
    #     write_to_excel(author, title, views, publish_date, description, url, channel_name)
    #     num = 1
    #     print(date_time() + "视频下载完成......")
    #     return num
    # else:
    #     single_video_write_to_excel(save_path, author, title, views, publish_date, description, url)


# 下载音频
def download_audio(yt, save_path, file_path):
    audio_streams = yt.streams.filter(only_audio=True, mime_type="audio/mp4") # 获取所有音频流
    sorted_audio_streams = sorted(audio_streams, key=lambda x: x.filesize, reverse=True) #print(audio_streams) print(audio)
    audio = sorted_audio_streams[0]  # 选择比特率最高的音频
    audio_name = 'Audio_' + remove_symbol(audio.default_filename.split(".")[0]) + '.' + \
                 audio.default_filename.split(".")[-1]
    completedfilesize = save_path + file_path + "/" + audio_name
    print("音频路径: " + completedfilesize)

    if file_exists_check(save_path + file_path + "/" + audio_name):
        # print("音频文件已下载，无需重新下载")
        result = check_file_download_completed(audio, completedfilesize, '音频')
        if result is False:
            print(date_time() + "下载的文件与油管文件大小不符,重新下载" + "音频")
            audio.download(output_path=save_path + file_path, filename=audio_name)
            return True
        return False
    else:
        audio.download(output_path=save_path + file_path, filename=audio_name)
        print(date_time() + "音频下载完成......")
        return True

# 创建文件夹
def file_path_check(save_path, file_path):
    dirs = save_path + file_path
    if not os.path.exists(dirs):
        print("新视频，正在创建新文件夹")
        os.makedirs(dirs)


# 下载视频封面file_path =author+"/"+title
def request_download(url, save_path, file_path, title):
    if file_exists_check(save_path + file_path + "/" + title + ".png"):
        # print("视频封面文件已下载，无需重新下载")
        return False
    else:
        r = requests.get(url)
        with open(save_path + file_path + "/" + title + ".png", 'wb') as f:
            f.write(r.content)
        print(date_time() + "视频封面下载完毕......")
        return True


# 重命名
def remove_symbol(word):
    word = re.sub('([^\u4e00-\u9fa5\u0030-\u0039\u0041-\u007a])', '', word)
    return word


# 文件存在校验
def file_exists_check(filePath):
    if os.path.exists(filePath):
        return True
    else:
        return False


# 格式话时间，精确到秒 %Y-%m-%d %H:%M:%S
def date_time():
    new_date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S ")
    return new_date_time


def author_name_check(author):
    if author == "Forest Film: camping, off grid cabin and bushcraft":
        author = "Forest Film"
        return author
    else:
        return author


def download_multi_video(urls):
    num = 1
    for url in urls:
        print("开始下载第" + str(num) + "个视频")
        downloadYoutube(url)
        num = num + 1
    print("批量下载完成，总共下载" + str(num) + "个视频")


'''
批量下载
'''


def download_by_channels(channe_lists):
    url = 'https://www.youtube.com/@'
    url_end = '/videos'
    num = 0
    sum_video_num = 0  # 本次总下载数
    up = ""
    download_type = 1  # 1为批量下载
    download_num = 3  # 循环下载up主的视频数
    for channel in channe_lists:
        video_num = 0  # 初始化视频下载数
        num = num + 1  # 初始化下载的推主序号
        channel_name = channel
        print(url + channel + url_end)
        channel = Channel(url + channel + url_end)
        print(channel.video_urls[:download_num])
        print("开始下载第" + str(num) + "个推主:" + channel.channel_name + " 最新的" + str(download_num) + "个视频")
        if len(channel.video_urls) != 0:
            for download_url in channel.video_urls[:download_num]:
                try:
                    video_num = video_num + downloadYoutube(download_url, download_type, channel_name)
                    print("test1")
                    if video_num != 0:
                        print("test2")
                        up += channel_name + " "
                    time.sleep(30)
                except Exception as e:
                    print("test3")
                    print(e)
                finally:
                    continue

        sum_video_num += video_num
        time.sleep(20)  # 每个推主中间停顿下

    print("批量下载完成，共查找" + str(num) + "个UP主,其中:" + up + "有新视频，总共下载下载了 " + str(sum_video_num) + " 视频。")


# 批量下载,可以下载的视频数量
def download_by_channels_by_num(channe_lists, download_num):
    url = 'https://www.youtube.com/@'
    url_end = '/videos'
    num = 0
    sum_video_num = 0  # 本次总下载数
    up = ""
    download_type = 1  # 1为批量下载
    for channel in channe_lists:
        video_num = 0  # 初始化视频下载数
        num = num + 1  # 初始化下载的推主序号
        channel_name = channel
        print(url + channel + url_end)
        channel = Channel(url + channel + url_end)
        print(channel.video_urls[:download_num])
        print("开始下载第" + str(num) + "个推主:" + channel.channel_name + " 最新的" + str(download_num) + "个视频")
        if len(channel.video_urls) != 0:
            for download_url in channel.video_urls[:download_num]:
                try:
                    video_num = video_num + downloadYoutube(download_url, download_type, channel_name)
                    if video_num != 0:
                        up += channel_name + " "
                    time.sleep(30)
                except Exception as e:
                    print(e)
                finally:
                    continue

        sum_video_num += video_num
        time.sleep(20)  # 每个推主中间停顿下

    print("批量下载完成，共查找" + str(num) + "个UP主,其中:" + up + "有新视频，总共下载下载了 " + str(sum_video_num) + " 视频。")


# 根据不同类型的推主放到不同文件夹
def save_path_check(channel_type):
    file_path_check(default_ptah, channel_type)
    result = default_ptah + channel_type + '/'
    return result


# 检查视频素材完整性如果没下载完，删除文件后重新下载
def check_file_download_completed(downloadfile, savedfile, type):
    completedfilesize = os.stat(savedfile).st_size
    print("已下载文件大小:" + str(subtitleUtil.pybyte(completedfilesize, 2)) + '\n' + "油管文件大小:" + str(
        subtitleUtil.pybyte(downloadfile.filesize, 2)))
    if completedfilesize == downloadfile.filesize:
        print(type + "文件已经完整下载")
        return True
    elif completedfilesize < downloadfile.filesize:
        print(type + "文件未完整下载，删除旧文件")
        return False


# 根据不同类型的推主放到不同excel
def excel_path_check(channel_type):
    excel_path = default_ptah + channel_type + '.xlsx'
    return excel_path


# 视频风格
def channel_type(channel_name):
    category_lists = {
        'camping': ['HikeCampClimb', 'AtikAilesi', 'BaumOutdoors', 'BahadirKlc',
                    'tahtarizkyorigma', 'WoodsOfSilence',
                    'Lonewolfwildcamping', 'ForestFilm', 'XanderBudnick',
                    'SBWildernessAdventures', 'BrooksandBirches',
                    'tabi-ie', 'HighlandWoodsman', 'Kampkolik', 'joinmeoutdoors',
                    '2withnature', 'forestsolitude7448',
                    'silentfamily', 'jaylegere', '365GunDogadayiz', 'LeavesDiary88'],
        'bushwalk': ['HarmenHoek', 'kraigadams'],
        'wild': ['ThisIsMyAlaska', 'BushcraftAdventure', 'NorwegianXplorer', 'Survivaland',
                 'MyMethead'],
        'cityview': ['IntotheWildFilms'],
        'reallife': ['johnnyharris'],
        'camera': ['snapsbyfox', 'MannyOrtiz', 'benjhaisch', 'LeeZavitz']
    }

    for category, channel_list in category_lists.items():
        if channel_name in channel_list:
            return category

    return None  # 如果没有匹配项，返回None或其他适当的值

def today_release_youtuber_list(url, download_type, channel_name):
    yt = get_yt(url)
    fuchsia = '\033[38;2;255;00;255m'  # color as hex #FF00FF
    reset_color = '\033[39m'
    # 配置信息
    author = remove_symbol(yt.author)  # 视频作者（不带空格）
    title = remove_symbol(yt.title)  # 视频标题(不带空格)
    save_path = save_path_check(channel_type(channel_name))
    file_path = author + "/" + yt.publish_date.strftime("%Y-%m-%d") + "_" + title
    print(f'\n' + fuchsia + '开始下载: ', author + "----" + title, '~ viewed', yt.views, 'times.')
    # 下载前先检查是否有该路径，没有则创建
    file_path_check(save_path, file_path)
    start = time.time()
    # 下载字幕
    subtitle = download_subtitles(yt, save_path, file_path, title)
    # 下载封面
    video_img = request_download(yt.thumbnail_url, save_path, file_path, title)  # 下载视频封面
    # 下载视频
    video_num = download_video(yt, save_path, file_path)
    # 下载音频
    audio = download_audio(yt, save_path, file_path)
    # 写入excel #转移到下载视频里
    # write_to_excel(save_path, yt.author, yt.title, yt.views, yt.publish_date, yt.description, url)
    end = time.time()
    if subtitle is True or video_img is True or video_num != 0 or audio is True:
        print(f'\n完成下载:  {title}' + "下载完成,共计花费了{:.2f}秒".format(end - start) + reset_color)
    else:
        print(f'\n====================本集视频素材均已下载====================')
    return video_num

def write_to_excel(author, title, views, publish_date, description, url, channel_name):
    lswb = xl.load_workbook(default_ptah + '临时文件.xlsx')  # 获取文件
    lstable = lswb.worksheets[0]  # 得到sheet页
    lsws = lswb.active
    lsnrows = lstable.max_row + 1  # 总行数
    lsws.cell(row=lsnrows, column=1, value=author)
    lsws.cell(row=lsnrows, column=2, value=title)
    lsws.cell(row=lsnrows, column=3, value=views)
    lsws.cell(row=lsnrows, column=4, value=publish_date.strftime("%Y%m%d"))
    lsws.cell(row=lsnrows, column=5, value=description)
    lsws.cell(row=lsnrows, column=6, value=author + " | " + title + "(第 期)")
    lsws.cell(row=lsnrows, column=7, value=url + "\r\n转自【" + author + "】")
    lswb.save(default_ptah + '临时文件.xlsx')
    execel_save_path = excel_path_check(channel_type(channel_name))
    print(execel_save_path)
    wb = xl.load_workbook(execel_save_path)  # 获取文件
    # table = wb.worksheets[0]  # 得到sheet页
    ws = wb[channel_name]
    # ws = ws.active
    nrows = ws.max_row + 1  # 总行数
    ws.cell(row=nrows, column=1, value=author)
    ws.cell(row=nrows, column=2, value=title)
    ws.cell(row=nrows, column=3, value=views)
    ws.cell(row=nrows, column=4, value=publish_date.strftime("%Y%m%d"))
    ws.cell(row=nrows, column=5, value=description)
    ws.cell(row=nrows, column=6, value=author + " | " + title + "(第 期)")
    ws.cell(row=nrows, column=7, value=url + "\r\n转自【" + author + "】")

    wb.save(execel_save_path)
    print("写入表格行 " + str(nrows) + ": " + author + title)
def tdownloadYoutube(url):
    yt = get_yt(url)
    fuchsia = '\033[38;2;255;00;255m'  # color as hex #FF00FF
    reset_color = '\033[39m'
    # 配置信息
    author = remove_symbol(yt.author)  # 视频作者（不带空格）
    title = remove_symbol(yt.title)  # 视频标题(不带空格)
    print("视频上传时间: " + yt.publish_date.strftime("%Y%m%d") + "\n" + "今天的日期: " + time.strftime("%Y%m%d"))
    save_path = save_path_check(channel_type(author))
    print("save_path:"+ save_path)
    file_path = author + "/" + yt.publish_date.strftime("%Y-%m-%d") + "_" + title
    print("file_path:"+ file_path)
    print(f'\n' + fuchsia + '开始下载: ', author + "----" + title, '~ viewed', yt.views, 'times.')
    # 下载前先检查是否有该路径，没有则创建
    file_path_check(save_path, file_path)
    start = time.time()
    # 下载字幕
    subtitle = tdownload_subtitles(yt, save_path, file_path, title)
    # 下载封面
    video_img = request_download(yt.thumbnail_url, save_path, file_path, title)  # 下载视频封面
    # 下载音频
    audio = download_audio(yt, save_path, file_path)
    # 下载视频
    video_num = download_video(yt, save_path, file_path)

    return video_num

def googleTrans(content):
    translator = Translator(service_urls=['translate.google.com.au'])  # 使用中国区域的Google翻译服务
    translation = translator.translate(content, dest='zh-cn')
    chinese_text = translation.text

    print(chinese_text)


def tdownload_subtitles(yt, save_path, file_path, title):
    print(yt.captions)


if __name__ == '__main__':
    # try:
    #     # 下载单个视频
    #     input_url=sys.argv[1]#视频连接
    #     downloadYoutube(input_url, 0, '')
    # except Exception as e:
    #     print(e)
    url = 'https://www.youtube.com/watch?v=d-uBQLHFLCs&ab_channel=AtikAilesi'
    default_ptah = get_path() + 'youtube/'
    print(default_ptah)
    #tdownloadYoutube(url)
    content = "Hello, how are you?"
    googleTrans(content)




