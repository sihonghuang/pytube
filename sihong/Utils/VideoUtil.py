import os
from moviepy.video.io.VideoFileClip import VideoFileClip
import time

def split_and_rename_video(input_path):
    start_time = time.time()  # 记录开始时间

    # Get the video file name without extension
    video_name, extension = os.path.splitext(os.path.basename(input_path))

    # Get the directory path of the input video
    input_dir = os.path.dirname(input_path)

    # Open the video using moviepy
    video = VideoFileClip(input_path)

    # Calculate the duration of each segment
    segment_duration = video.duration / 3

    for i in range(3):
        start_time_segment = time.time()  # 记录分段处理开始时间

        start_time = i * segment_duration
        end_time = (i + 1) * segment_duration

        # Extract the segment and save it
        segment = video.subclip(start_time, end_time)
        output_path = os.path.join(input_dir, f"{video_name}_{i + 1}{extension}")
        segment.write_videofile(output_path, codec="libx264")

        end_time_segment = time.time()  # 记录分段处理结束时间
        segment_processing_time = end_time_segment - start_time_segment
        print(f"Segment {i + 1} processing time: {segment_processing_time:.2f} seconds")

    # Close the video object
    video.reader.close()
    video.audio.reader.close_proc()

    end_time = time.time()  # 记录结束时间
    total_processing_time = end_time - start_time
    print(f"Total processing time: {total_processing_time:.2f} seconds")

if __name__ == '__main__':
    # Example usage:
    input_video_path = input("要分隔的视频")
    split_and_rename_video(input_video_path)
