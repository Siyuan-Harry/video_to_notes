#给videos改名
import os
from moviepy.editor import VideoFileClip
import whisper
import datetime
from datetime import timedelta, datetime
import cv2
import re
import streamlit as st
import tempfile

ss = st.session_state

def initialize_file(added_files):
    temp_file_paths = []
    with st.spinner('Processing file...'): 
        for added_file in added_files:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".md") as tmp:
                        tmp.write(added_file.getvalue())
                        tmp_path = tmp.name
            temp_file_paths.append(tmp_path)
    st.success('Processing file...Done')
    return temp_file_paths

def rename_file():

    # 视频文件夹路径
    video_folder_path = '/content/cs224n_videos'

    # 获取视频文件夹中所有.mp4文件
    video_files = sorted([f for f in os.listdir(video_folder_path) if f.endswith('.mp4')])

    # 按顺序重命名文件
    for index, video_file in enumerate(video_files, start=1):
        # 创建新的文件名，格式为 "001-...-....mp4"
        new_file_name = f"{index:03d}-{video_file}"

        # 获取旧的文件完整路径
        old_file_path = os.path.join(video_folder_path, video_file)

        # 获取新的文件完整路径
        new_file_path = os.path.join(video_folder_path, new_file_name)

        # 重命名文件
        os.rename(old_file_path, new_file_path)
        print(f"Renamed '{video_file}' to '{new_file_name}'")

    print("Renaming complete.")

def extract_audio():
    # 设置视频文件夹路径
    video_folder_path = '/content/cs224n_videos'
    audio_folder_path = '/content/cs224n_audios'

    # 如果音频输出文件夹不存在，就创建它
    if not os.path.isdir(audio_folder_path):
        os.makedirs(audio_folder_path)

    # 获取所有.mp4文件
    video_files = [f for f in os.listdir(video_folder_path) if f.endswith('.mp4')]

    for video_file in video_files:
        # 完整的视频文件路径
        video_path = os.path.join(video_folder_path, video_file)

        # 音频文件名，替换文件扩展名
        audio_file = video_file.replace('.mp4', '.mp3')

        # 目标音频文件路径，确保路径使用合适的文件夹分隔符
        audio_path = os.path.join(audio_folder_path, audio_file)

        # 加载视频文件
        video_clip = VideoFileClip(video_path)

        # 从视频剪辑提取音频
        audio_clip = video_clip.audio

        # 将音频写入.mp3文件，确保目标文件夹存在
        audio_clip.write_audiofile(audio_path)

        # 关闭剪辑
        video_clip.close()
        audio_clip.close()

        print(f"提取的音频已保存至: {audio_path}")


def timedelta_to_srt_time(timedelta):
    """将datetime.timedelta对象转换为SRT时间格式。"""
    total_seconds = int(timedelta.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    milliseconds = int(timedelta.microseconds / 1000)
    return '{:02}:{:02}:{:02},{:03}'.format(hours, minutes, seconds, milliseconds)

def make_srt(transcription):
    """生成SRT格式的字幕。"""
    segments = transcription["segments"]
    srt_entries = []
    for i, segment in enumerate(segments, start=1):
        start = timedelta_to_srt_time(datetime.timedelta(seconds=segment["start"]))
        end = timedelta_to_srt_time(datetime.timedelta(seconds=segment["end"]))
        text = segment["text"].strip()
        entry = f"{i}\n{start} --> {end}\n{text}\n"
        srt_entries.append(entry)
    return "\n".join(srt_entries)

# 转写，并生成为srt格式
def generate_srt():

    #设置目标文件夹
    audio_folder_path = '/content/cs224n_audios'
    srt_folder_path = '/content/cs224n_srts'

    # 如果SRT输出文件夹不存在，就创建它
    if not os.path.isdir(srt_folder_path):
        os.makedirs(srt_folder_path)

    # 转录音频文件
    model = whisper.load_model("small") #model可以调整

    # 获取所有.mp3文件
    audio_files = [f for f in os.listdir(audio_folder_path) if f.endswith('.mp3')]

    # 转写并生成SRT文件
    for audio_file in audio_files:
        audio_path = os.path.join(audio_folder_path, audio_file)
        srt_filename = audio_file.replace('.mp3', '.srt')
        srt_path = os.path.join(srt_folder_path, srt_filename)

        # 进行转写
        result = model.transcribe(audio_path)

        # 生成SRT内容
        srt_content = make_srt(result)

        # 写入SRT文件
        with open(srt_path, "w", encoding="utf-8") as f:
            f.write(srt_content)

        print(f"SRT字幕已生成并保存至：{srt_path}")

# 每隔30秒钟截一张图
# filename: save_screenshots.py

# Function to ensure the output directory exists
def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def make_screenshots():
    video_folder_path = 'cs224n_videos'
    video_files = [f for f in os.listdir(video_folder_path) if f.endswith('.mp4')]

    # Read the video frame by frame
    for video_file in video_files:

        # Open the video file
        vc = cv2.VideoCapture(f"{video_folder_path}/{video_file}")

        # Check if the video was opened successfully
        if not vc.isOpened():
            print("Error: Could not open video.")
            exit()

        # Get the frames per second (fps) of the video
        fps = vc.get(cv2.CAP_PROP_FPS)

        # Calculate the number of frames to skip to take a screenshot every 30 seconds
        frame_interval = int(fps * 30)

        # Directory where screenshots will be saved
        output_directory = f'notes/screenshots/{video_file[:3]}'
        ensure_dir(output_directory)

        # Frame counter
        frame_count = 0
        # Screenshot counter
        screenshot_count = 1
        while True:
            ret, frame = vc.read()
            if not ret:
                break

            # If the current frame is at the specified interval, save it as an image
            if frame_count % frame_interval == 0:
                # Construct image file path
                image_path = os.path.join(output_directory, f'Screenshot{screenshot_count}.jpg')
                # Save the image
                cv2.imwrite(image_path, frame)
                # Print information about the saved screenshot
                print(f"Screenshot{screenshot_count} saved at frame {frame_count}")
                screenshot_count += 1

            frame_count += 1

        # Release the video capture object
        vc.release()
        print('')
    print("All screenshots have been saved.")

#create_text_picture_manuscript👇

# Function to extract the numeric part of the screenshot file name
def extract_number(filename):
    match = re.search(r'Screenshot(\d+)', filename)
    return int(match.group(1)) if match else -1

# Function to parse the srt file
def parse_srt(filepath):
    with open(filepath, 'r') as f:
        content = f.read().strip()
    pattern = re.compile(r'(\d+)\n(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n(.*?)\n\n', re.DOTALL)
    entries = [
        (int(match.group(1)), match.group(2), match.group(3), match.group(4))
        for match in pattern.finditer(content)
    ]
    return entries

# Function to parse the time format of srt to a datetime object
def parse_srt_time(time_str):
    time_parts = time_str.split(',')
    time_parts[1] = "0"*(3-len(time_parts[1])) + time_parts[1] # Padding milliseconds to 3 digits if needed
    return datetime.strptime(','.join(time_parts), '%H:%M:%S,%f')

# Function to create the markdown file
def create_markdown(srt_file, srt_entries, screenshots, output_file):
    srt_start_times = [parse_srt_time(start) for _, start, _, _ in srt_entries]

    # Assuming the first screenshot was taken at the time the first subtitle appears
    base_time = srt_start_times[0] if srt_start_times else datetime.min
    screenshot_times = [base_time + timedelta(seconds=30) * i for i in range(len(screenshots))]

    # Find the nearest srt entry index to the given screenshot time
    def find_nearest_srt_index(screenshot_time):
        return max(0, min(len(srt_entries)-1,
            next((i for i, start_time in enumerate(srt_start_times) if start_time > screenshot_time), len(srt_entries) - 1) - 1
        ))

    screenshot_entries = [(find_nearest_srt_index(screenshot_time), screenshot_time, screenshot) for screenshot_time, screenshot in zip(screenshot_times, screenshots)]

    with open(output_file, 'w') as md:
        last_written = -1
        for srt_index, _, screenshot in screenshot_entries:
            # Write subtitles up to current screenshot
            for entry in srt_entries[last_written + 1: srt_index + 1]:
                _, _, _, text = entry
                md.write(f"{text}\n\n")
            # Write screenshot
            md.write(f"![](screenshots/{srt_file[:3]}/{screenshot})\n\n")
            last_written = srt_index

        # Write any remaining subtitles after the last screenshot
        for entry in srt_entries[last_written + 1:]:
            _, _, _, text = entry
            md.write(f"{text}\n\n")

def create_text_picture_manuscript():
    # Paths for files and folders
    screenshots_folder = 'notes/screenshots'
    srt_folder_path = 'cs224n_srts'
    srt_files = [f for f in os.listdir(srt_folder_path) if f.endswith('.srt')]

    # Parse SRT file

    for srt_file in srt_files:
        srt_entries = parse_srt(f"{srt_folder_path}/{srt_file}")

        #精准对应好截图的文件夹
        screenshots = sorted(os.listdir(f"{screenshots_folder}/{srt_file[:3]}"),
                            key=lambda filename: extract_number(filename))
        output_markdown_file = f"notes/{srt_file[:3]}_note.md"

        create_markdown(srt_file, srt_entries, screenshots, output_markdown_file)

        # Output the manuscript creation message
        print(f"Manuscript with text-picture mixed content has been created: {output_markdown_file}")


def app():
    st.title('videoReader v0.0.1')
    st.markdown("""
        <style>
            .footer {
                position: fixed;
                bottom: 0;
                right: 10px;
                width: auto;
                background-color: transparent;
                text-align: right;
                padding-right: 10px;
                padding-bottom: 10px;
            }
        </style>
        <div class="footer">Made with 🧡 by Siyuan</div>
    """, unsafe_allow_html=True)
    with st.sidebar:
        st.image("https://siyuan-harry.oss-cn-beijing.aliyuncs.com/oss://siyuan-harry/20231021212525.png")
        added_files = st.file_uploader('Upload .md or .pdf files, simultaneous mixed upload these types is supported.', type=['.md','.pdf'], accept_multiple_files=True)