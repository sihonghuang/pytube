import youtube_dl

def list_all_audio_formats(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'listformats': True,
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            formats = info['formats']

            print("所有音频格式：")
            for f in formats:
                if f['acodec'] != 'none' and f.get('vcodec') is None:
                    print(f"{f['format_id']} - {f['ext']} - {f['acodec']} - {f['abr']}k")

        except Exception as e:
            print(f"获取音频格式失败：{e}")

if __name__ == "__main__":
    # 视频链接
    video_url = 'https://www.youtube.com/watch?v=bY-kUpNFucs&t=1s&ab_channel=AtikAilesi'

    # 调用函数列出所有音频格式
    list_all_audio_formats(video_url)


