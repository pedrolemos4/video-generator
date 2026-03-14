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

    SOURCE_VIDEO = "../videos/minecraft-parkour.mp4"

    TITLE_WIDTH = 2000
    TITLE_HEIGHT = 900

    TTS_PAD_START = 0.3
    PAD_END = 0.5

    OUTPUT_DIR = Path("../output")

    WHISPER_MODEL = "small"

    DEFAULT_VOICE = "en-US-AriaNeural"

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
