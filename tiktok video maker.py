import praw
import moviepy.editor as mp
import boto3
import speech_recognition as sr
import time
import random
import os
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip
from moviepy.video.tools.drawing import color_gradient


# Set the path to the ImageMagick convert executable
os.environ["IMAGEMAGICK_BINARY"] = r"C:\path\to\convert.exe"

# Function to generate Reddit story and output to story.txt
def generate_reddit_story(client_id, client_secret, user_agent, subreddit_name):
    reddit = praw.Reddit(client_id=client_id,
                         client_secret=client_secret,
                         user_agent=user_agent)
    subreddit = reddit.subreddit(subreddit_name)
    top_submissions = list(subreddit.top(time_filter='day', limit=25))  # Fetch top 25 submissions
    random_submission = random.choice(top_submissions)  # Pick a random submission from the top 25
    with open("input.txt", "w") as f:
        f.write(random_submission.title + "\n")
        f.write(random_submission.selftext)

# Function to convert text to speech using Amazon Polly
def convert_text_to_speech(input_file, output_file, aws_access_key_id, aws_secret_access_key, aws_region):
    polly_client = boto3.client('polly', aws_access_key_id=aws_access_key_id,
                                aws_secret_access_key=aws_secret_access_key,
                                region_name=aws_region)

    with open(input_file, 'r') as f:
        text = f.read()

    # Split text into smaller chunks (each chunk not exceeding 1500 characters)
    chunks = [text[i:i+1500] for i in range(0, len(text), 1500)]

    # Synthesize each chunk separately
    with open(output_file, 'wb') as f:
        for chunk in chunks:
            response = polly_client.synthesize_speech(Text=chunk, OutputFormat='mp3', VoiceId='Matthew')
            f.write(response['AudioStream'].read())

# Function to convert MP3 to WAV
def convert_mp3_to_wav(mp3_file, wav_file):
    sound = mp.AudioFileClip(mp3_file)
    sound.write_audiofile(wav_file)

# Function to overlay audio onto video
def overlay_audio(video_file, audio_file, output_file):
    video = mp.VideoFileClip(video_file)
    audio = mp.AudioFileClip(audio_file)

    # Ensure video is longer than audio
    if video.duration < audio.duration + 5:  # Add 5 seconds leeway
        raise ValueError("Audio duration exceeds video duration")

    # Randomly select start time for video clip
    start_time = random.uniform(0, video.duration - audio.duration - 5)  # Subtract 5 seconds for leeway

    # Extract video segment with sufficient duration
    video_segment = video.subclip(start_time, start_time + audio.duration + 5)

    # Concatenate video and audio
    final_clip = mp.concatenate_videoclips([video_segment.set_audio(audio)])

    # Write the final video file
    final_clip.write_videofile(output_file, codec="libx264", audio_codec="aac", fps=24)

# Function to clean up generated files
def clean_up():
    files_to_delete = ['input.txt, output.mp3', 'output.wav', 'output_with_audio.mp4']
    for file in files_to_delete:
        if os.path.exists(file):
            os.remove(file)

if __name__ == "__main__":
    # Generate Reddit story
    generate_reddit_story(client_id="dEg1nhh2fwfIpZ43OSmMZQ",
                          client_secret="LZk7RlWM34LAB36n9qAu9li0ZYWtYQ",
                          user_agent="gen",
                          subreddit_name="stories")
    time.sleep(1)  # Adding a 1-second delay

    # Convert text to speech
    input_file = 'input.txt'
    output_file_mp3 = 'output.mp3'
    convert_text_to_speech(input_file, output_file_mp3,
                           aws_access_key_id='AKIAXAASOZVYNXQIQS5H',
                           aws_secret_access_key='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',
                           aws_region='us-west-2')
    time.sleep(1)  # Adding a 1-second delay

    # Convert MP3 to WAV
    output_file_wav = 'output.wav'
    convert_mp3_to_wav(output_file_mp3, output_file_wav)
    time.sleep(1)  # Adding a 1-second delay

    # Overlay audio onto video
    overlay_audio('video.mp4', output_file_wav, 'output_with_audio.mp4')
    time.sleep(1)  # Adding a 1-second delay

    # Rename output_with_audio.mp4 to output.mp4
    os.rename('output_with_audio.mp4', 'output.mp4')

    # Clean up generated files
    clean_up()
    
def add_caption_to_video(video_path, caption_text, caption_duration=5, output_path="output_video.mp4"):
    # Load the video
    video_clip = VideoFileClip(video_path)
# Create a text clip with the caption
caption_text = "input.txt"
video_path = "output.mp4"

#!/usr/bin/env python3

import os
import argparse
import platform
import subprocess
from datetime import timedelta

try:
    import whisper
    import yt_dlp
    from moviepy.editor import VideoFileClip, CompositeVideoClip, TextClip
    from moviepy.video.tools.subtitles import SubtitlesClip
except ImportError:
    print("trying to install dependencies")

    def install_libraries():
        required_libraries = ['whisper', 'yt_dlp', 'moviepy']
        current_os = platform.system()
        
        if current_os == 'Windows':
            package_manager = 'pip'
        elif current_os == 'Darwin':
            package_manager = 'pip3'
        elif current_os == 'Linux':
            package_manager = 'pip3'
        else:
            print("unsupported operating system, skipping install")
            return
        
        for library in required_libraries:
            try:
                subprocess.check_call([package_manager, 'install', library])
                print(f"{library} installed successfully, run the script again")
            except subprocess.CalledProcessError:
                print(f"failed to install {library}")
                exit()

    install_libraries()

YT_ATTACH = "youtube-a"
YT_GENERATE = "youtube-g"
VALID_MODES = ("attach", "generate", YT_ATTACH, YT_GENERATE)
YT_MODES = (YT_ATTACH, YT_GENERATE)
TEMP_FILE = "temp.mp3"
OUTPUT_SRT = "output.srt"
OUTPUT_VID = "output.mp4"
YT_VID = "yt.mp4"


class VideoManager:
    def __init__(self, path: str, youtube: bool) -> None:
        self.path = path
        self.youtube = youtube
        if not self.youtube:
            self.video = VideoFileClip(path)

        self.extract_audio()

    def download(self) -> None:
        ydl_opts = {
            "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "outtmpl": "yt",
        }
        with yt_dlp.YoutubeDL(ydl_opts) as dl:
            dl.download([self.path])

        self.video = VideoFileClip(YT_VID)

    def extract_audio(self) -> None:
        if self.youtube:
            self.download()

        if self.video.audio is not None:
            self.video.audio.write_audiofile("temp.mp3", codec="mp3")
        else:
            print("video has no audio, quitting")


class Utility:
    def __init__(self, path: str, youtube: bool) -> None:
        self.path = path
        self.youtube = youtube

    def file_exists(self) -> bool:
        if self.youtube:
            return True
        return len(self.path) > 0 and os.path.exists(path=self.path)


class SubtitleGenerator:
    def __init__(self, videomanager: VideoManager) -> None:
        self.videomanager = videomanager

    def generate(self) -> None:
        # Credit goes to
        # https://github.com/openai/whisper/discussions/98#discussioncomment-3725983
        # github.com/lectair

        model = whisper.load_model("base")
        transcribe = model.transcribe(audio=TEMP_FILE, fp16=False)
        segments = transcribe["segments"]

        for seg in segments:
            start = str(0) + str(timedelta(seconds=int(seg["start"]))) + ",000"
            end = str(0) + str(timedelta(seconds=int(seg["end"]))) + ",000"
            text = seg["text"]
            segment_id = seg["id"] + 1
            segment = f"{segment_id}\n{start} --> {end}\n{text[1:] if text[0] == ' ' else text}\n\n"
            with open(OUTPUT_SRT, "a", encoding="utf-8") as f:
                f.write(segment)

        print("subtitles generated")

    def attach(self) -> None:
        self.generate()
        if os.path.exists(OUTPUT_SRT):
            subtitles = SubtitlesClip(
                OUTPUT_SRT,
                lambda txt: TextClip(
                    txt,
                    font="Arial",
                    fontsize=24,
                    color="white",
                    bg_color="black",
                ),
            )

            video_with_subtitles = CompositeVideoClip(
                [
                    self.videomanager.video,
                    subtitles.set_position(("center", 0.95), relative=True),
                ]
            )

            video_with_subtitles.write_videofile(OUTPUT_VID, codec="libx264")
            print(f"saved to {OUTPUT_VID}")

def check_ffmpeg() -> bool:
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        return result.returncode == 0 and 'ffmpeg' in result.stdout
    except FileNotFoundError:
        return False


def main() -> None:
    parser = argparse.ArgumentParser(description="auto caption generator v1.0")
    parser.add_argument(
        "mode", metavar="mode", type=str, help="operation mode (attach|generate)"
    )
    parser.add_argument("path", metavar="path", type=str, help="filepath of the video")
    args = parser.parse_args()
    mode = args.mode
    path = args.path

    if not check_ffmpeg():
        print("ffmpeg must be installed to run this script, quitting")
        exit()

    if len(mode) > 0 and len(path) > 0:
        yt_mode = True if mode in YT_MODES else False
        utility = Utility(path, yt_mode)

        if mode in VALID_MODES and utility.file_exists():
            videomanager = VideoManager(utility.path, yt_mode)
            subtitle_generator = SubtitleGenerator(videomanager)

            if mode == VALID_MODES[0] or mode == VALID_MODES[2]:
                subtitle_generator.attach()
            elif mode == VALID_MODES[1] or mode == VALID_MODES[3]:
                subtitle_generator.generate()
        else:
            print("invalid mode or file path, quitting")


if __name__ == "__main__":
    main()




