import googletrans
import youtube_dl
import os
import re
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips
import subprocess
def translate_english_to_chinese(text):
    translator = googletrans.Translator(service_urls=['translate.google.com/?sl=auto&tl=zh-CN&op=translate'])
    translation = translator.translate(text, src='en', dest='zh-cn')
    return translation.text

def clean_filename(filename):
    # 过滤文件名中的特殊字符
    return re.sub(r'[\\/:*?"<>|]', '', filename)

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
    audio_ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(save_path, file_path, 'Audio_%(title)s.%(ext)s')
    }

    with youtube_dl.YoutubeDL(audio_ydl_opts) as ydl:
        audio_info = ydl.extract_info(url, download=False)
        audio_file_path = os.path.join(save_path, file_path, f"Audio_{clean_filename(audio_info['title'])}.{audio_info['ext']}")
        audio_size = audio_info.get('filesize', 0)

        if not check_file_exists_and_size(audio_file_path, audio_size):
            print(f"开始下载音频：{audio_file_path}")
            ydl.download([url])
        else:
            print(f"音频文件已存在或大小符合要求，跳过下载：{audio_file_path}")

    video_ydl_opts = {
        'format': 'bestvideo[ext=mp4]',
        'outtmpl': os.path.join(save_path, file_path, 'Video_%(title)s.%(ext)s')
    }

    with youtube_dl.YoutubeDL(video_ydl_opts) as ydl:
        video_info = ydl.extract_info(url, download=False)
        video_file_path = os.path.join(save_path, file_path, f"Video_{clean_filename(video_info['title'])}.{video_info['ext']}")
        video_size = video_info.get('filesize', 0)

        if not check_file_exists_and_size(video_file_path, video_size):
            print(f"开始下载视频：{video_file_path}")
            ydl.download([url])
        else:
            print(f"视频文件已存在或大小符合要求，跳过下载：{video_file_path}")

    print("视频和音频下载完成")
    if not os.path.exists(os.path.join(save_path, file_path,
                                       f"Merged_{clean_filename(video_info['title'])}.mp4")):
        # 合并音视频文件
        audio_file = os.path.join(save_path, file_path,
                                  f"Audio_{clean_filename(audio_info['title'])}.{audio_info['ext']}")
        video_file = os.path.join(save_path, file_path,
                                  f"Video_{clean_filename(video_info['title'])}.{video_info['ext']}")
        merged_file = os.path.join(save_path, file_path,
                                   f"Merged_{clean_filename(video_info['title'])}.mp4")

        # 使用 ffmpeg 合并音视频文件
        cmd = f'ffmpeg -i "{video_file}" -i "{audio_file}" -c:v copy -c:a aac "{merged_file}"'
        subprocess.run(cmd, shell=True)

        print(f"音频和视频文件已合并为：{merged_file}")
    else:
        print(f"合并后的文件已存在，跳过合并")

def get_video_audio_formats(url):
    ydl_opts = {'format': 'best'}
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        formats = info['formats']
        video_formats = [f for f in formats if f.get('vcodec') is not None]
        audio_formats = [f for f in formats if f.get('acodec') is not None]

        return video_formats, audio_formats

if __name__ == '__main__':
    # # 示例用法
    # english_text = "Hello, how are you?"
    # translated_text = translate_english_to_chinese(english_text)
    # print(translated_text)
    # 使用示例
    video_url = 'https://www.youtube.com/watch?v=rcW43O_hL90'
    save_path = 'D:/油管视频/'  # 修改为保存视频的路径
    file_path = 'videos'  # 修改为视频文件夹路径
    download_highest_resolution_video(video_url, save_path, file_path)
    video_formats, audio_formats = get_video_audio_formats(video_url)
    print("视频格式：")
    for video in video_formats:
        print(video['format'], video['ext'])

    print("音频格式：")
    for audio in audio_formats:
        print(audio['format'], audio['ext'])
