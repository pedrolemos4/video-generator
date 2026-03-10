#!/usr/bin/env python3
"""
pipeline/merger.py
------------------
Final video assembly: merges video segment, TTS audio, and burned-in subtitles.
Instantiated with subtitle style and padding so they are set once per project.
"""

from pathlib import Path

from utils.utils import Utils
from utils.global_variables import Variables


class Merger:

    def __init__(
        self,
        pad_start: float = Variables.PAD_START,
        subtitle_style: str = Variables.SUBTITLE_STYLE,
    ):
        self.pad_start = pad_start
        self.subtitle_style = subtitle_style

    def merge(
        self,
        video_path: Path,
        audio_path: Path,
        srt_path: Path,
        output_path: Path,
    ) -> None:
        """
        Combine video segment, TTS audio, and burned-in subtitles into
        the final output video.

        Audio is delayed by pad_start seconds using -itsoffset so it starts
        after the silent lead-in. Subtitles should already be offset by
        pad_start (handled in Subtitles.build).
        """
        Utils.log("Merging video + audio + subtitles into final output", "🎞")

        srt_abs = str(srt_path.resolve()).replace("\\", "/")

        Utils.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                str(video_path),
                "-itsoffset",
                str(self.pad_start),
                "-i",
                str(audio_path),
                "-filter_complex",
                f"[0:v]subtitles='{srt_abs}':force_style='{self.subtitle_style}'[v]",
                "-map",
                "[v]",
                "-map",
                "1:a",
                "-c:v",
                "libx264",
                "-c:a",
                "aac",
                "-preset",
                "fast",
                "-crf",
                "23",
                "-movflags",
                "+faststart",
                str(output_path),
            ],
            "Rendering final video",
        )

        Utils.log(f"Final video saved: {output_path}", "🎉")
