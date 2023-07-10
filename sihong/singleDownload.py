# 获取以下内容并写入excel
# 作者/标题/浏览量/日期/描述/链接
from urllib.error import HTTPError, URLError
import self as self
from pytube import YouTube
from pytube.cli import on_progress
import time
import os
import requests
import re
import datetime
from pytube import Channel
import sys

import subtitleUtil

fuchsia = '\033[38;2;255;00;255m'  # color as hex #FF00FF
reset_color = '\033[39m'
# 配置区
win_path = "/home"  # TODO
default_file_ptah = win_path + '/youtube/'  # excel默认保存露营 # TODO
channel_type_dict = {'camping': '露营', 'bushwalk': '徒步', 'wild': '户外',
                     'cityview': '街景', 'reallife': '真人秀', 'camera': '相机', 'null': '临时文件'}  # TODO




def downloadYoutube(url, download_type, channel_name):
    yt = get_yt(url)
    # 配置信息
    author = remove_symbol(yt.author)  # 视频作者（不带空格）
    title = remove_symbol(yt.title)  # 视频标题(不带空格)
    video_type = channel_type_dict[channel_type(author)]  # 视频分类名称
    save_path = default_file_ptah + video_type + '/'
    file_path = author + "/" + yt.publish_date.strftime("%Y-%m-%d") + "_" + title
    print("视频上传时间: " + yt.publish_date.strftime("%Y%m%d") + "\n" + "今天的日期: " + time.strftime("%Y%m%d"))
    print(f'\n' + fuchsia + '开始下载: ', author + "----" + title, '~ viewed', yt.views, 'times.')

    # 下载前先检查是否有该路径，没有则创建
    file_path_check(save_path, file_path)
    start = time.time()
    # 下载字幕
    #subtitle = download_subtitles(yt, save_path, file_path, title)
    subtitle = False
    # 下载封面
    #video_img = request_download(yt.thumbnail_url, save_path, file_path, title)  # 下载视频封面
    video_img = False
    # 下载音频
    #audio = download_audio(yt, save_path, file_path)
    audio = False
    # 下载视频
    video_num = download_video(yt, save_path, file_path)
    # video_num = 0
    # 写入excel #转移到下载视频里
    end = time.time()
    print("subtitle: " + str(subtitle), " video_img:" + str(video_img), " video_num:" + str(video_num),
          " audio:" + str(audio) + "\r\n")
    if subtitle is True or video_img is True or video_num is True or audio is True:
        print(f'\n完成下载:  {title}' + "下载完成,共计花费了{}秒".format(end - start) + reset_color)
        return True
    else:
        print(f'\n====================本集视频素材均已下载====================')
        return False


#获取YouTube下载
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


#下载字幕
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
    video = yt.streams.filter(adaptive=True).filter(mime_type='video/webm').first()  # 选择清晰度最高的视频
    video_name = 'Video_' + remove_symbol(video.default_filename.split(".")[0]) + '.' + \
                 video.default_filename.split(".")[-1]
    completedfilesize = save_path + file_path + "/" + video_name
    print("清晰度最高的视频:" + str(
        yt.streams.filter(adaptive=True).filter(mime_type='video/webm').first()) + '\r\n' +
          str(yt.streams.filter(adaptive=True).filter(
              mime_type='video/mp4').first()))
    #print("视频路径: " + save_path + file_path + "/" + video_name)
    if file_exists_check(save_path + file_path + "/" + video_name):
        # print("视频文件已下载，判断是否需要重新下载")
        result = check_file_download_completed(video, completedfilesize, '视频')
        if result is False:
            print("下载的文件与油管文件大小不符,重新下载")
            video.download(output_path=save_path + file_path, filename=video_name)
            return True
        else:
            return False
    else:
        string = subtitleUtil.pybyte(video.filesize, 2)
        print(date_time() + "未下载过,开始下载视频,视频大小 %s ......" % string)
        video.download(output_path=save_path + file_path, filename=video_name)
        return True

# 下载音频
def download_audio(yt, save_path, file_path):
    audio = yt.streams.filter(only_audio=True).first()  # 选择比特率最高的音频
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




# 视频风格
def channel_type(channel_name):

    result = 'null'
    camping_lsit = ['HikeCampClimb', 'AtikAilesi', 'BaumOutdoors', 'BahadirKlc', 'tahtarizkyorigma', 'WoodsOfSilence',
                    'Lonewolf902', 'ForestFilm', 'XanderBudnick', 'SBWildernessAdventures', 'BrooksBirches',
                    'tabi-ie', 'HighlandWoodsman', 'Kampkolik', 'JoinMeOutdoors', 'TwowithNature', 'forestsolitude7448',
                    'SilentFamily', 'jaylegere', '365GnDoadayz', 'LeavesDiary','ForestFilmCampingHotTentLogCabin']  # 露营

    bushwalk_list = ['HarmenHoek', 'kraigadams']  # 徒步

    wild_list = ['ThisIsMyAlaska', 'BushcraftAdventure', 'NorwegianXplorer', 'Survivaland',
                 'MyMethead']  # 野外生存

    cityview_list = ['IntotheWildFilms']  # 街景

    reallife_list = ['johnnyharris']  # 真人秀

    camera_list = ['snapsbyfox', 'MannyOrtiz', 'BenjHaisch', 'LeeZavitz','RomanFox']  # 相机

    for lst_name, lst in [("camping_lsit", camping_lsit), ("bushwalk_list", bushwalk_list), ("wild_list", wild_list),
                          ("cityview_list", cityview_list), ("reallife_list", reallife_list),
                          ("camera_list", camera_list)]:
        if channel_name in lst:
            result = lst_name.split('_')[0]
            break
    print("***********推主:" + channel_name," 结果: "+result+"***********")
    return result


def today_release_youtuber_list(url, download_type, channel_name):
    yt = get_yt(url)
    fuchsia = '\033[38;2;255;00;255m'  # color as hex #FF00FF
    reset_color = '\033[39m'
    # 配置信息
    author = remove_symbol(yt.author)  # 视频作者（不带空格）
    title = remove_symbol(yt.title)  # 视频标题(不带空格)
    video_type = channel_type_dict[channel_type(author)]  # 视频分类名称
    save_path = default_file_ptah + video_type + '/'
    file_path = author + "/" + yt.publish_date.strftime("%Y-%m-%d") + "_" + title
    print(f'\n' + fuchsia + '开始下载: ', author + "----" + title, '~ viewed', yt.views, 'times.')
    # 下载前先检查是否有该路径，没有则创建
    file_path_check(save_path, file_path)
    start = time.time()
    # 下载字幕
    subtitle = download_subtitles(yt, save_path, file_path, title)
    # 下载封面
    #video_img = request_download(yt.thumbnail_url, save_path, file_path, title)  # 下载视频封面
    video_img = False
    # 下载视频
    video_num = download_video(yt, save_path, file_path, yt.author, yt.title, yt.views, yt.publish_date, yt.description,
                               url, download_type, channel_name)
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

if __name__ == '__main__':
    try:
        # 下载单个视频
        input_url=sys.argv[1]#视频连接
        downloadYoutube(input_url, 0, '')
    except Exception as e:
        print(e)




