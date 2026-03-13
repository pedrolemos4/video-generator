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

    async def generate_with_padding(
        self, story: str, title: str, output_path: Path
    ) -> None:
        f"""Generate TTS audio with {Variables.TTS_PAD_START} silence prepended."""
        tmp_path = output_path.with_suffix(".tmp.mp3")
        await self.generate_no_padding(story, title, tmp_path)

        Utils.run(
            [
                "ffmpeg",
                "-y",
                "-f",
                "lavfi",
                "-i",
                "anullsrc=r=24000:cl=mono",
                "-i",
                str(tmp_path),
                "-filter_complex",
                f"[0]atrim=duration={Variables.TTS_PAD_START}[silence];[silence][1]concat=n=2:v=0:a=1",
                str(output_path),
            ],
            f"Adding {Variables.TTS_PAD_START} silence padding to audio",
        )

        tmp_path.unlink()

    async def generate_no_padding(
        self, story: str, title: str, output_path: Path
    ) -> None:
        """Generate TTS audio with no padding."""
        import edge_tts

        Utils.log(f"Generating TTS with voice: {self.voice}", "🗣")

        processed = re.sub(r"([.!?])\s+", r"\1 .. ", story)
        processed = f"{title} ... {processed}"

        communicate = edge_tts.Communicate(processed, self.voice)
        await communicate.save(str(output_path))
        Utils.log(f"TTS audio saved: {output_path}", "✅")
