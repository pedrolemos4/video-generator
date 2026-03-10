#!/usr/bin/env python3
"""
_pipeline/tts.py
---------------
Text-to-speech generation using edge-tts with SSML.

build_ssml() and list_voices() are static — pure functions with no state.
generate() is an async instance method — voice is set at init so it
can be reused across multiple story generations without repeating the arg.
"""

import html
import re
import subprocess
from pathlib import Path

from utils.utils import Utils
from utils.global_variables import Variables


class TTS:

    EXPRESSIVE_VOICES = {
        "en-US-AriaNeural": "narration-professional",
        "en-US-JennyNeural": "chat",
        "en-US-GuyNeural": "narration-professional",
    }

    def __init__(self, voice: str = Variables.DEFAULT_VOICE):
        self.voice = voice

    @staticmethod
    def build_ssml(story: str, voice: str) -> str:
        """
        Wrap plain story text in SSML for expressive, human-sounding speech.
        - pitch="+8%"    slight lift to avoid flat monotone
        - rate="-5%"     gentle slowdown for clarity
        - break 450ms    pause after . ! ? (sounds like breathing)
        - break 200ms    pause after , ; (natural phrasing rhythm)
        - express-as     activates neural voice emotional engine where supported
        """
        escaped = html.escape(story)
        escaped = re.sub(r"([.!?])\s+", r'\1<break time="450ms"/> ', escaped)
        escaped = re.sub(r"([,;])\s+", r'\1<break time="200ms"/> ', escaped)

        style = TTS.EXPRESSIVE_VOICES.get(voice)

        if style:
            inner = (
                f'<mstts:express-as style="{style}">'
                f'<prosody pitch="+8%" rate="-5%">{escaped}</prosody>'
                f"</mstts:express-as>"
            )
        else:
            inner = f'<prosody pitch="+8%" rate="-5%">{escaped}</prosody>'

        return (
            '<speak version="1.0" '
            'xmlns="http://www.w3.org/2001/10/synthesis" '
            'xmlns:mstts="https://www.w3.org/2001/mstts" '
            f'xml:lang="en-US"><voice name="{voice}">'
            f"{inner}"
            "</voice></speak>"
        )

    @staticmethod
    def list_voices() -> None:
        """Print all available edge-tts voices to stdout."""
        result = subprocess.run(
            ["edge-tts", "--list-voices"], capture_output=True, text=True
        )
        print(result.stdout)

    async def generate(self, story: str, output_path: Path) -> None:
        """Generate TTS audio from story text and save to output_path."""
        import edge_tts

        Utils.log(f"Generating TTS with voice: {self.voice}", "🗣")
        ssml = TTS.build_ssml(story, self.voice)
        Utils.log(
            "SSML applied: pitch variation + sentence pauses + expressive style", "🎭"
        )

        communicate = edge_tts.Communicate(ssml, self.voice)
        await communicate.save(str(output_path))
        Utils.log(f"TTS audio saved: {output_path}", "✅")
