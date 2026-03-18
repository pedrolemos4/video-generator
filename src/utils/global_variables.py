#!/usr/bin/env python3
"""
global_variables.py
---------
Central configuration for the Video Story Pipeline.

Usage:
    from config import Config

    print(Config.SOURCE_VIDEO)
    print(Config.DEFAULT_VOICE)
"""

from pathlib import Path


class Variables:
    # Set at start
    TELEGRAM_BOT_TOKEN = ""
    TELEGRAM_CHANNEL_ID = ""

    # Static
    ACRONYM = "SH"
    USERNAME = "The Story Hub"

    TITLE_WIDTH = 2000
    TITLE_HEIGHT = 900

    TTS_PAD_START = 0.3
    PAD_END = 0.5

    OUTPUT_DIR = Path("../output")

    WHISPER_MODEL = "small"

    DEFAULT_SOURCE_VIDEO = "../videos/csgo-surf-1.mp4"
    BACKGROUND_VIDEOS = [
        DEFAULT_SOURCE_VIDEO,
        "../videos/minecraft-parkour-1.mp4",
        "../videos/minecraft-parkour-2.mp4",
    ]

    DEFAULT_VOICE = "en-US-AriaNeural"
    VOICES = [
        DEFAULT_VOICE,  # Female, expressive & natural
        "en-US-ChristopherNeural",  # Male, deep & authoritative
        "en-US-EricNeural",  # Male, calm & clear
        "en-US-GuyNeural",  # Male, natural & warm
        "en-US-JennyNeural",  # Female, friendly & conversational
        "en-US-MichelleNeural",  # Female, warm & engaging
        "en-GB-RyanNeural",  # Male British, smooth & cinematic
        "en-GB-SoniaNeural",  # Female British, clear & elegant
        "en-AU-WilliamNeural",  # Male Australian, relaxed & deep
        "en-AU-NatashaNeural",  # Female Australian, warm & natural
    ]

    SUBTITLE_FONT_SIZE = 12
    SUBTITLE_STYLE = (
        f"FontSize={SUBTITLE_FONT_SIZE},"
        "FontName=Arial,"
        "Bold=1,"
        "PrimaryColour=&H00FFFFFF,"
        "OutlineColour=&H00000000,"
        "Outline=2,"
        "Shadow=1,"
        "Alignment=2,"
        "MarginV=40"
    )

    MIN_CLIP_DURATION = 60  # seconds — never cut below this
