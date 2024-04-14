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
    generate_reddit_story(client_id="ID",
                          client_secret="ID",
                          user_agent="gen",
                          subreddit_name="stories")
    time.sleep(1)  # Adding a 1-second delay

    # Convert text to speech
    input_file = 'input.txt'
    output_file_mp3 = 'output.mp3'
    convert_text_to_speech(input_file, output_file_mp3,
                           aws_access_key_id='ID',
                           aws_secret_access_key='ID',
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




