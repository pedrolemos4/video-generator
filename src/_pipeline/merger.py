#!/usr/bin/env python3
"""
pipeline/merger.py
------------------
Final video assembly: merges video segment, TTS audio, and burned-in subtitles.
"""

from pathlib import Path

from _pipeline.title.title_card import TitleCard
from utils.utils import Utils
from utils.global_variables import Variables


class Merger:

    def __init__(self, subtitle_style: str = Variables.SUBTITLE_STYLE):
        self.subtitle_style = subtitle_style

    async def merge(
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
            title_card_path = output_path.with_suffix(".title.png")
            await TitleCard.render(title, title_card_path)

            filter_complex = (
                f"[0:v]subtitles='{srt_abs}':force_style='{self.subtitle_style}'[subs];"
                f"[subs][2:v]overlay=(W-w)/2:(H-h)/2:enable='between(t,0,10)'[v]"
            )

            Utils.run(
                [
                    "ffmpeg",
                    "-y",
                    "-i",
                    str(video_path),
                    "-i",
                    str(audio_path),
                    "-i",
                    str(title_card_path),
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

            title_card_path.unlink()

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
