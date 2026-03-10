#!/usr/bin/env python3
"""
_pipeline/transcriber.py
-----------------------
Audio transcription using local Whisper or whisper-ctranslate2.
Instantiated with model and language so they are set once per project.
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

from utils.utils import Utils
from utils.global_variables import Variables


class Transcriber:

    def __init__(self, model: str = Variables.WHISPER_MODEL, language: str = "en"):
        self.model = model
        self.language = language

    def transcribe(self, audio_path: Path) -> dict:
        """
        Transcribe an audio file using Whisper and return JSON output
        with word-level timestamps.

        Tries whisper-ctranslate2 first (faster on CPU),
        falls back to openai-whisper automatically.
        """
        Utils.log(f"Transcribing audio with Whisper ({self.model} model)...", "📝")

        whisper_cmd = None
        for cmd in ["whisper-ctranslate2", "whisper"]:
            result = subprocess.run(["which", cmd], capture_output=True)
            if result.returncode == 0:
                whisper_cmd = cmd
                break

        if not whisper_cmd:
            print(
                "ERROR: Neither whisper nor whisper-ctranslate2 found.", file=sys.stderr
            )
            sys.exit(1)

        Utils.log(f"Using: {whisper_cmd}", "🔍")

        with tempfile.TemporaryDirectory() as tmpdir:
            Utils.run(
                [
                    whisper_cmd,
                    str(audio_path),
                    "--model",
                    self.model,
                    "--output_format",
                    "json",
                    "--word_timestamps",
                    "true",
                    "--language",
                    self.language,
                    "--output_dir",
                    tmpdir,
                ],
                "Running transcription",
            )

            json_files = list(Path(tmpdir).glob("*.json"))
            if not json_files:
                print("ERROR: Whisper produced no JSON output.", file=sys.stderr)
                sys.exit(1)

            with open(json_files[0]) as f:
                return json.load(f)
