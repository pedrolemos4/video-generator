#!/usr/bin/env python3
"""
_pipeline/tts.py
---------------
Text-to-speech generation using edge-tts.
Pauses are added manually by preprocessing the text.
"""

import re
import subprocess
from pathlib import Path

from utils.utils import Utils
from utils.global_variables import Variables


class TTS:

    def __init__(self, voice: str = Variables.DEFAULT_VOICE):
        self.voice = voice

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

        # Manually add pauses at sentence and clause boundaries
        processed = re.sub(r"([.!?])\s+", r"\1 ... ", story)
        processed = re.sub(r"([,;])\s+", r"\1 .. ", processed)

        communicate = edge_tts.Communicate(
            processed,
            self.voice,
        )
        await communicate.save(str(output_path))
        Utils.log(f"TTS audio saved: {output_path}", "✅")
