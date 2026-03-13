#!/usr/bin/env python3
"""
_pipeline/tts.py
----------------
Text-to-speech generation using piper-tts.
Runs fully offline, no API key needed.
Voices are downloaded at startup by VoiceDownloader.
"""

from pathlib import Path

from utils.utils import Utils
from utils.global_variables import Variables
from infrastrucure.piper_voice import PiperVoice


class TTS:

    def __init__(self, voice: PiperVoice = Variables.DEFAULT_VOICE):
        self.voice = voice

    @staticmethod
    def list_voices() -> None:
        """Print all available voices from the PiperVoice enum."""
        for voice in PiperVoice:
            Utils.log(f"{voice.name} — {voice.value}", "🎙")

    async def generate(self, story: str, output_path: Path) -> None:
        import wave
        from piper.voice import PiperVoice as PiperVoiceLib

        Utils.log(f"Generating TTS with voice: {self.voice.value}", "🗣")

        voice = PiperVoiceLib.load(self.voice.model_path)

        with wave.open(str(output_path), "wb") as wav_file:
            voice.synthesize(story, wav_file)

        Utils.log(f"TTS audio saved: {output_path}", "✅")
