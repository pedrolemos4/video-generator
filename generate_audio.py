from io import BytesIO
import os
from langdetect import detect
from gtts import gTTS
from pydub import AudioSegment
from moviepy.editor import *

MAX_TIME_DURATION_SECONDS = 65


def detect_language(text):
    try:
        language = detect(text)
        return language
    except Exception as e:
        print(f"Error detecting language: {e}")
        return None


from moviepy.editor import *


def split_audio(audio_path, number):
    audioclip = AudioFileClip(audio_path)

    files_name = []
    total_duration = audioclip.duration
    start_time = 0
    end_time = MAX_TIME_DURATION_SECONDS
    segment_index = 1

    while start_time < total_duration:
        if end_time > total_duration:
            end_time = total_duration

        # Create subclip
        subclip = audioclip.subclip(start_time, end_time)

        # Define output file name (adjust as needed)
        output_file = f".\\generated-audios\\output-{number}-part-{segment_index}.wav"

        # Export subclip to file
        subclip.write_audiofile(output_file)

        files_name.append(output_file)

        # Update times for next iteration
        start_time = end_time
        end_time += MAX_TIME_DURATION_SECONDS
        segment_index += 1

    # Close the audioclip to free up resources
    audioclip.close()
    return files_name


def generate_audio(text: str):
    files = os.listdir(".\\generated-audios")
    numbers_final = [
        int(file.replace("output-", "").replace(".wav", ""))
        for file in files
        if file.startswith("output") and file.endswith(".wav")
    ]

    if not numbers_final:
        next_number_final = 1
    else:
        next_number_final = max(numbers_final) + 1

    language = detect_language(text)
    tts = gTTS(text=text, lang=language)

    path = (
        f"C:\\Repos\\video-generator\\generated-audios\\output-{next_number_final}.mp3"
    )
    tts.save(path)

    audioclip = AudioFileClip(path)
    audioclip = audioclip.fx(vfx.speedx, 1.2)

    output_filename = f".\\generated-audios\\output-{next_number_final}.wav"

    audioclip.write_audiofile(output_filename)

    os.remove(path)

    if audioclip.duration > MAX_TIME_DURATION_SECONDS:
        return split_audio(output_filename, next_number_final)

    return [output_filename]
