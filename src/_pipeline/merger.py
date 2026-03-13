#!/usr/bin/env python3
"""
pipeline/merger.py
------------------
Final video assembly: merges video segment, TTS audio, and burned-in subtitles.
"""

from pathlib import Path

from utils.utils import Utils
from utils.global_variables import Variables


class Merger:

    def __init__(self, subtitle_style: str = Variables.SUBTITLE_STYLE):
        self.subtitle_style = subtitle_style

    def merge(
        self,
        video_path: Path,
        audio_path: Path,
        srt_path: Path,
        output_path: Path,
        title: str = None,
    ) -> None:
        Utils.log("Merging video + audio + subtitles into final output", "🎞")

        srt_abs = str(srt_path.resolve()).replace("\\", "/")

        if title:
            filter_complex = (
                f"[0:v]subtitles='{srt_abs}':force_style='{self.subtitle_style}'[subs];"
                f"[subs]drawtext=text='{title}'"
                f":fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
                f":fontsize=36"
                f":fontcolor=white"
                f":borderw=2"
                f":bordercolor=black"
                f":x=(w-text_w)/2"
                f":y=(h-text_h)/2[v]"
            )
        else:
            filter_complex = (
                f"[0:v]subtitles='{srt_abs}':force_style='{self.subtitle_style}'[v]"
            )

        Utils.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                str(video_path),
                "-i",
                str(audio_path),
                "-filter_complex",
                filter_complex,
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
