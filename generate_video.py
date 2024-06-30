import math
import random
from faster_whisper import WhisperModel
from moviepy.editor import *
import pysrt


def format_time(seconds):
    hours = math.floor(seconds / 3600)
    seconds %= 3600
    minutes = math.floor(seconds / 60)
    seconds %= 60
    milliseconds = round((seconds - math.floor(seconds)) * 1000)
    seconds = math.floor(seconds)
    formatted_time = f"{hours:02d}:{minutes:02d}:{seconds:01d},{milliseconds:03d}"

    return formatted_time


def transcribe(audio):
    model = WhisperModel("small")
    segments, info = model.transcribe(audio)
    language = info[0]
    print("Transcription language", info[0])
    segments = list(segments)
    for segment in segments:
        print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))
    return language, segments


def generate_subtitle_file(filename, language, segments):

    subtitle_file = f".\\generated-subtitles\\sub-{filename}.{language}.srt"
    text = ""
    for index, segment in enumerate(segments):
        segment_start = format_time(segment.start)
        segment_end = format_time(segment.end)
        text += f"{str(index+1)} \n"
        text += f"{segment_start} --> {segment_end} \n"
        text += f"{segment.text} \n"
        text += "\n"

    f = open(subtitle_file, "w")
    f.write(text)
    f.close()

    return subtitle_file


def wrap_text(text):
    max_width = 30
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        if current_line and len(current_line) + len(word) + 1 > max_width:
            lines.append(current_line)
            current_line = word
        else:
            if current_line:
                current_line += " "
            current_line += word
    lines.append(current_line)

    return "\n".join(lines)


def generate_video(audio_path: str):
    video_directory = ".\\videos\\"
    target_width = 1080
    target_height = 1920

    # Get a list of all video files in the directory
    video_files = [
        f
        for f in os.listdir(video_directory)
        if os.path.isfile(os.path.join(video_directory, f))
    ]

    # Choose a random video file
    random_video_file = random.choice(video_files)

    videoclip = VideoFileClip(video_directory + random_video_file)
    audioclip = AudioFileClip(audio_path)

    list_audio_path = audio_path.split("\\")
    filename = list_audio_path[-1].replace(".wav", "")

    input_path_name = f".\\generated-videos\\{filename}.mp4"

    language, segments = transcribe(audio_path)

    subtitle_file = generate_subtitle_file(filename, language, segments)
    subtitles = pysrt.open(subtitle_file)

    subtitle_clips = []
    for subtitle in subtitles:
        wrapped_text = wrap_text(subtitle.text)  # Wrap text at 30 characters per line
        txt_clip = TextClip(
            wrapped_text,
            fontsize=70,  # Increase fontsize
            color="white",
            # bg_color="black",
            font="Arial",
            size=(target_width - 80, None),  # Add padding to fit within video width
        )
        txt_clip = txt_clip.set_position(
            ("center", target_height - 400)
        )  # Position higher
        txt_clip = txt_clip.set_start(subtitle.start.seconds)
        txt_clip = txt_clip.set_duration(subtitle.end.seconds - subtitle.start.seconds)
        txt_clip = txt_clip.margin(bottom=20, opacity=0)  # Add margin from the bottom
        subtitle_clips.append(txt_clip)

    # subtitle_clips = [
    #     TextClip(
    #         str(subtitle.text),
    #         fontsize=50,  # Adjust fontsize as needed
    #         color="white",
    #         bg_color="black",
    #         size=(target_width - 40, None),  # Add padding to fit within video width
    #     )
    #     .set_position("center", "bottom")
    #     .set_start(subtitle.start.seconds)
    #     .set_duration(subtitle.end.seconds - subtitle.start.seconds)
    #     .margin(bottom=20, opacity=0)
    #     for subtitle in subtitles
    # ]

    new_audioclip = CompositeAudioClip([audioclip])
    videoclip.audio = new_audioclip

    new_videoclip = CompositeVideoClip([videoclip] + subtitle_clips)

    # new_videoclip = CompositeVideoClip(
    #     [videoclip]
    #     + [
    #         TextClip(str(subtitle.text), fontsize=24, color="white", bg_color="black")
    #         .set_position("center", "bottom")
    #         .set_start(subtitle.start.seconds)
    #         .set_duration(subtitle.end.seconds - subtitle.start.seconds)
    #         for subtitle in subtitles
    #     ]
    # )

    new_videoclip.duration = audioclip.duration
    new_videoclip.size = (target_width, target_height)

    new_videoclip.write_videofile(input_path_name, fps=24)
