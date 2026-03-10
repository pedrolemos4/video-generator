#!/usr/bin/env python3
"""
utils.py
--------
Reusable utilities for shell command execution, logging, and media inspection.

Usage:
    from utils import Pipeline

    Pipeline.log("Starting process")
    result = Pipeline.run(["ffmpeg", "-version"])
    duration = Pipeline.get_duration(Path("video.mp4"))
"""

import subprocess
import sys
from pathlib import Path


class Utils:

    @staticmethod
    def log(msg: str, emoji: str = "▶") -> None:
        """Print a styled log message to stdout."""
        print(f"\n{emoji}  {msg}", flush=True)

    @staticmethod
    def run(cmd: list, desc: str = "") -> subprocess.CompletedProcess:
        """
        Run a shell command and return the result.
        Prints desc as a log line before running if provided.
        Exits the process with an error message if the command fails.
        """
        if desc:
            Utils.log(desc, "⚙")
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"  ERROR: {result.stderr.strip()}", file=sys.stderr)
            sys.exit(1)
        return result

    @staticmethod
    def get_duration(path: Path) -> float:
        """
        Return the duration in seconds of any media file (video or audio)
        using ffprobe. Requires ffmpeg to be installed.
        """
        result = Utils.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "csv=p=0",
                str(path),
            ]
        )
        return float(result.stdout.strip())
