#!/usr/bin/env python3
"""
pipeline/video.py
-----------------
Video segment extraction from a long source file.
Instantiated with padding config so it is set once per project.
"""

import random
import sys
from pathlib import Path

from utils.utils import Utils
from utils.global_variables import Variables


class Video:

    def __init__(
        self,
        pad_end: float = Variables.PAD_END,
    ):
        self.pad_end = pad_end

    def cut_segment(
        self,
        source: Path,
        audio_duration: float,
        output_path: Path,
    ) -> None:
        """
        Pick a random start point in the source video and cut a segment of:
            audio_duration + pad_start + pad_end

        Timeline of the resulting clip:
            [0 → pad_start]                     silent lead-in
            [pad_start → pad_start+audio]        audio + subtitles
            [→ end]                              silent tail

        Uses stream copy (-c copy): fast, lossless, no re-encoding.
        """
        source_duration = Utils.get_duration(source)
        clip_duration = audio_duration + self.pad_end

        if source_duration < clip_duration:
            print(
                f"ERROR: Source video ({source_duration:.1f}s) is shorter than "
                f"required clip length ({clip_duration:.1f}s).",
                file=sys.stderr,
            )
            sys.exit(1)

        max_start = source_duration - clip_duration
        cut_start = random.uniform(0, max_start)
        cut_end = cut_start + clip_duration

        Utils.log(
            f"Random cut: {cut_start:.2f}s → {cut_end:.2f}s  "
            f"| clip: {clip_duration:.2f}s  "
            f"| audio: {audio_duration:.2f}s  "
            f"| padding: +{0}s / +{self.pad_end}s",
            "✂️",
        )

        Utils.run(
            [
                "ffmpeg",
                "-y",
                "-ss",
                f"{cut_start:.6f}",
                "-t",
                f"{clip_duration:.6f}",
                "-i",
                str(source),
                "-c",
                "copy",
                str(output_path),
            ],
            "Cutting video segment (stream copy, no re-encode)",
        )

        Utils.log(f"Video segment saved: {output_path}", "✅")
