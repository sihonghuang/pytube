import os

from sihong.Utils import commonUtil, subtitleUtil
import requests
import re
from youtube_transcript_api import YouTubeTranscriptApi
import youtube_dl
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips
import subprocess


# 下载视频封面
def request_download(url, save_path, file_path, title):
    if commonUtil.file_exists_check(save_path + file_path + "/" + title + ".png"):
        # print("视频封面文件已下载，无需重新下载")
        return False
    else:
        r = requests.get(url)
        with open(save_path + file_path + "/" + title + ".png", 'wb') as f:
            f.write(r.content)
        print(commonUtil.date_time() + "视频封面下载完毕......")
        return True


# 下载音频
def download_audio(yt, save_path, file_path):
    print(commonUtil.get_time() + "开始下载音频")
    audio_streams = yt.streams.filter(only_audio=True, mime_type="audio/mp4")  # 获取所有音频流
    sorted_audio_streams = sorted(audio_streams, key=lambda x: x.filesize,
                                  reverse=True)  # print(audio_streams) print(audio)
    audio = sorted_audio_streams[0]  # 选择比特率最高的音频
    audio_name = 'Audio_' + commonUtil.remove_symbol(
        audio.default_filename.split(".")[0]) + '.' + \
                 audio.default_filename.split(".")[-1]
    completedfilesize = save_path + file_path + "/" + audio_name

    if commonUtil.file_exists_check(save_path + file_path + "/" + audio_name):
        # print("音频文件已下载，无需重新下载")
        result = commonUtil.check_file_download_completed(audio, completedfilesize, '音频')
        if result is False:
            print(commonUtil.date_time() + "下载的文件与油管文件大小不符,重新下载" + "音频")
            audio.download(output_path=save_path + file_path, filename=audio_name)
            return True
        return False
    else:
        print("音频路径: " + completedfilesize)
        audio.download(output_path=save_path + file_path, filename=audio_name)
        print(commonUtil.date_time() + "音频下载完成......")
        return True


def download_caption(url, save_path, file_path, title):
    download = False
    video_url = url.replace("https://www.youtube.com/watch?v=", "")
    transcript_list = YouTubeTranscriptApi.list_transcripts(video_url)
    CHStranscript = ""
    ENtrranscript = ""
    # print(transcript_list)
    for transcript in transcript_list:
        caption_list = {'English': 'en', 'English (auto-generated)': 'a.en', 'Chinese': 'zh',
                        'Chinese (Simplified)': 'zh-Hans', 'Chinese (Taiwan)': 'zh-TW',
                        'Chinese (China)': 'zh-CN', 'English (United States)': 'en-US',
                        'English (United Kingdom)': 'en-GB'}  # 'English': 'en',
        for language in caption_list:
            if transcript.language == language:
                captionfile = save_path + file_path + "/" + caption_list[
                    language] + title + " (" + caption_list[language] + ").srt"
                if commonUtil.file_exists_check(captionfile):
                    print(language + " 字幕文件已下载，无需重新下载")
                else:
                    srt = YouTubeTranscriptApi.get_transcript(video_url,
                                                              languages=[
                                                                  caption_list[language]])
                    srt_content = convert_to_srt(srt)
                    with open(captionfile, "w", encoding="utf-8") as f:
                        f.write(srt_content)
                    f.close()
                    print(language + " 字幕文件下载完成")
                    download = True
                    if is_contains(captionfile, " (en)"):
                        ENtrranscript = subtitleUtil.changeEnglishSubtitles(captionfile)
                    elif is_contains(captionfile, " (zh-Hans)") or is_contains(captionfile,
                                                                               " (zh)"):
                        CHStranscript = subtitleUtil.changeChineseSubtitles(captionfile)
    if ENtrranscript and CHStranscript:
        subtitleUtil.merge_caption(CHStranscript, ENtrranscript)
    return download


def is_contains(filename, field):
    basename = os.path.basename(filename)
    return field in basename


def convert_to_srt(transcript_list):
    srt = ""
    for i, item in enumerate(transcript_list, start=1):
        start_time = format_time(item["start"])
        end_time = format_time(item["start"] + item["duration"])
        line = f"{i}\n{start_time} --> {end_time}\n{item['text']}\n\n"
        srt += line
    return srt


def format_time(seconds):
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return "{:02d}:{:02d}:{:06.3f}".format(int(hours), int(minutes), seconds)


# 下载字幕
def download_subtitles(yt, save_path, file_path, title):
    num = 0
    print(commonUtil.get_time() + "开始下载字幕")
    # check if captions are available for the video
    if yt.captions:
        # print available captions languages
        print("Available captions languages:")
        for lang in yt.captions.keys():
            print(lang)
        caption_list = {'English': 'en', 'English (auto-generated)': 'a.en', 'Chinese': 'zh',
                        'Chinese (Simplified)': 'zh-Hans', 'Chinese (Taiwan)': 'zh-TW',
                        'Chinese (China)': 'zh-CN',
                        'English (United States)': 'en-US',
                        'English (United Kingdom)': 'en-GB'}  # 'English': 'en',
        for language in caption_list:
            for caption in yt.caption_tracks:
                if language == caption.name:
                    print(language)
                    caption_list_caption_name = caption_list[caption.name].replace(".", "")
                    print(caption_list_caption_name)
                    if commonUtil.file_exists_check(
                        save_path + file_path + "/" + caption_list_caption_name + title + " (" +
                        caption_list[
                            language] + ").srt"):
                        # print(language + "字幕文件已下载，无需重新下载")
                        return True
                    else:
                        yt.captions[caption_list[caption.name]].download(
                            title=caption_list[caption.name] + title,
                            output_path=save_path + file_path, srt=True)

                        print(language + "字幕下载完毕......")
                else:
                    continue
            if num == 0:
                return True
            else:
                return False
    else:
        print("Captions are not available for this video.")
        return False


# 下载视频
def download_video(yt, save_path, file_path):
    print(commonUtil.get_time() + "开始下载视频")
    num = 0
    print(yt.streams.get_by_itag(299))
    video_streams = yt.streams.filter(file_extension='mp4')  # 获取所有的视频流（筛选出文件扩展名为mp4的流）
    sorted_streams = sorted(video_streams, key=lambda stream: stream.filesize,
                            reverse=True)  # 根据文件大小进行排序
    video = sorted_streams[0]
    # video = yt.streams.filter(adaptive=True).filter(mime_type='video/webm').first()  # 选择清晰度最高的视频
    video_name = 'Video_' + commonUtil.remove_symbol(
        video.default_filename.split(".")[0]) + '.' + video.default_filename.split(".")[-1]
    completedfilesize = save_path + file_path + "/" + video_name
    print(commonUtil.get_time() + "视频路径: " + save_path + file_path + "/" + video_name)
    if commonUtil.file_exists_check(save_path + file_path + "/" + video_name):
        result = commonUtil.check_file_download_completed(video, completedfilesize, '视频')
        if result is False:
            print(commonUtil.get_time() + "下载的文件与油管文件大小不符,重新下载")
            video.download(output_path=save_path + file_path, filename=video_name)
            num = 1
            return num
        else:
            return num
    else:
        string = subtitleUtil.pybyte(video.filesize, 2)
        print(commonUtil.get_time() + "未下载过,开始下载视频,视频大小 %s ......" % string)
        video.download(output_path=save_path + file_path, filename=video_name)


def get_video_description(url):
    full_html = requests.get(url).text
    y = re.search(r'shortDescription":"', full_html)
    desc = ""
    count = y.start() + 19  # adding the length of the 'shortDescription":"
    while True:
        # get the letter at current index in text
        letter = full_html[count]
        if letter == "\"":
            if full_html[count - 1] == "\\":
                # this is case where the letter before is a backslash, meaning it is not real end of description
                desc += letter
                count += 1
            else:
                break
        else:
            desc += letter
            count += 1
    return desc


def check_file_exists_and_size(file_path, required_size):
    # 检查文件是否存在，并获取文件大小
    if os.path.exists(file_path):
        file_size = os.path.getsize(file_path)
        return file_size >= required_size
    return False


def merge_audio_and_video(audio_file_path, video_file_path, output_file_path):
    # 合并音频和视频文件
    audio_clip = AudioFileClip(audio_file_path)
    video_clip = VideoFileClip(video_file_path)
    video_with_audio_clip = video_clip.set_audio(audio_clip)
    video_with_audio_clip.write_videofile(output_file_path, codec='libx264')


def download_highest_resolution_video(url, save_path, file_path):
    # 检查是否已经存在名为1.txt的文件
    check_file_path = os.path.join(save_path, file_path, "1.txt")
    if os.path.exists(check_file_path):
        print("完整视频已下载。")
    else:
        video_ydl_opts = {
            #'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'format': 'bestvideo[ext=mp4]',
            'outtmpl': os.path.join(save_path, file_path, 'Video_%(title)s.%(ext)s')
        }
        audio_ydl_opts = {
            'format': 'bestaudio[ext=m4a]',  # 只下载原始音频文件
            'writesubtitles': False,  # 禁用自动生成的字幕
            'outtmpl': os.path.join(save_path, file_path, 'Audio_%(title)s.%(ext)s'),
            'quiet': False,  # 设置为True时不输出下载信息
            'nocheckcertificate': True,  # 忽略SSL证书检查，如果下载过程中报错可以尝试添加该选项
        }
        try:
            # 下载视频
            with youtube_dl.YoutubeDL(video_ydl_opts) as ydl:
                video_info = ydl.extract_info(url, download=False)
                video_title = commonUtil.remove_symbol(video_info['title'])
                video_file_path = os.path.join(save_path, file_path, f"Video_{video_title}.mp4")
                print("video_file_path:" + video_file_path)
                video_size = video_info.get('filesize', 0)

                if not check_file_exists_and_size(video_file_path, video_size):
                    print(f"开始下载视频：{video_file_path}")
                    ydl.download([url])
                    # 下载完成后将文件重命名
                    os.rename(
                        os.path.join(save_path, file_path, f"Video_{video_info['title']}.mp4"),
                        video_file_path)
                else:
                    print(f"视频文件已存在或大小符合要求，跳过下载：{video_file_path}")
            # 下载音频
            with youtube_dl.YoutubeDL(audio_ydl_opts) as ydl:
                audio_info = ydl.extract_info(url, download=False)
                audio_title = commonUtil.remove_symbol(audio_info['title'])
                audio_file_path = os.path.join(save_path, file_path,
                                               f"Audio_{audio_title}.{audio_info['ext']}")
                print("audio_file_path:" + audio_file_path)
                audio_size = audio_info.get('filesize', 0)

                if not check_file_exists_and_size(audio_file_path, audio_size):
                    print(f"开始下载音频：{audio_file_path}")
                    ydl.download([url])
                    # 下载完成后将文件重命名
                    os.rename(os.path.join(save_path, file_path,
                                           f"Audio_{audio_info['title']}.{audio_info['ext']}"),
                              audio_file_path)
                else:
                    print(f"音频文件已存在或大小符合要求，跳过下载：{audio_file_path}")
        except Exception as e:
            print(f"视频下载失败: {e}")
        else:
            print("视频下载完成！")
        # 合并视频和音频为最终视频文件
        final_output = os.path.join(save_path, file_path, f"Final_{video_title}.mp4")
        # 检查最终输出文件是否存在，如果不存在，则进行合并操作
        if not os.path.exists(final_output):
            merge_video_and_audio(video_file_path, audio_file_path, final_output)
            # 删除原始的视频和音频文件
            os.remove(video_file_path)
            os.remove(audio_file_path)
            with open(check_file_path, "w") as f:
                f.write("Video and audio merged successfully.")# 创建名为1.txt的文件
                f.close()
        else:
            print(f"最终输出文件已存在，跳过下载合并：{final_output}")


def check_file_exists_and_size(file_path, size_threshold):
    if os.path.exists(file_path):
        if size_threshold > 0:
            return os.path.getsize(file_path) >= size_threshold
        else:
            return True
    return False


def merge_video_and_audio(video_path, audio_path, output_path):
    try:
        subprocess.run(
            ['ffmpeg', '-i', video_path, '-i', audio_path, '-c:v', 'copy', '-c:a', 'aac',
             output_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"合并视频和音频失败：{e}")
    else:
        print("视频合并完成！")


if __name__ == '__main__':
    url = 'https://www.youtube.com/watch?v=d-uBQLHFLCs&t=2s&ab_channel=AtikAilesi'
    download_highest_resolution_video(url, 'D:/油管资料/露营/',
                                      'AtikAilesi/2023-06-02_DDETLDOLUYAIINDAIRMAKKENARINDAKAMP')
