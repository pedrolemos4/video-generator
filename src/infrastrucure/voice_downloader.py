#!/usr/bin/env python3
"""
infrastructure/voice_downloader.py
------------------------------
Downloads all PiperVoice model files at startup.
Call VoiceDownloader.download_all() from main.py before starting the API.
"""

import urllib.request
from pathlib import Path

from infrastrucure.piper_voice import PiperVoice
from utils.utils import Utils


class VoiceDownloader:

    VOICES_DIR = Path("/app/voices")

    @staticmethod
    def download_all() -> None:
        """Download all voices defined in PiperVoice enum if not already present."""
        VoiceDownloader.VOICES_DIR.mkdir(parents=True, exist_ok=True)

        for voice in PiperVoice:
            VoiceDownloader._download_voice(voice)

    @staticmethod
    def _download_voice(voice: PiperVoice) -> None:
        model_path = Path(voice.model_path)
        config_path = Path(voice.config_path)

        if model_path.exists() and config_path.exists():
            Utils.log(f"Voice already downloaded: {voice.value}", "✅")
            return

        Utils.log(f"Downloading voice: {voice.value}", "⬇️")

        urllib.request.urlretrieve(voice.download_url, model_path)
        urllib.request.urlretrieve(voice.config_url, config_path)

        Utils.log(f"Voice downloaded: {voice.value}", "✅")
