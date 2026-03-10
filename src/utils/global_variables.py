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

    SOURCE_VIDEO = "../../videos/minecraft-parkour.mp4"

    PAD_START = 0.5
    PAD_END = 0.5

    OUTPUT_DIR = Path("../../output")

    WHISPER_MODEL = "small"

    DEFAULT_VOICE = "en-US-AriaNeural"

    SUBTITLE_STYLE = (
        "FontSize=22,"
        "FontName=Arial,"
        "Bold=1,"
        "PrimaryColour=&H00FFFFFF,"
        "OutlineColour=&H00000000,"
        "Outline=2,"
        "Shadow=1,"
        "Alignment=2,"
        "MarginV=40"
    )
