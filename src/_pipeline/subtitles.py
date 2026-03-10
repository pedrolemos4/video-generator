#!/usr/bin/env python3
"""
pipeline/subtitles.py
---------------------
SRT subtitle generation from Whisper transcript output.
All methods are static — pure transformations with no state.
"""

import sys
import textwrap
from pathlib import Path

from utils.utils import Utils


class Subtitles:

    @staticmethod
    def ms_to_srt_time(seconds: float) -> str:
        """Convert seconds (float) to SRT timestamp HH:MM:SS,mmm"""
        ms = int((seconds % 1) * 1000)
        s = int(seconds) % 60
        m = int(seconds // 60) % 60
        h = int(seconds // 3600)
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

    @staticmethod
    def build(
        transcript: dict,
        output_path: Path,
        offset: float = 0.0,
        words_per_line: int = 8,
    ) -> None:
        """
        Build an SRT file from Whisper JSON transcript output.

        offset:         shifts all timestamps forward (set to PAD_START
                        so subtitles sync with the delayed audio)
        words_per_line: words grouped per subtitle entry
        """
        Utils.log("Building SRT subtitle file", "📄")

        all_words = []
        for segment in transcript.get("segments", []):
            for word in segment.get("words", []):
                text = word.get("word", "").strip()
                if text:
                    all_words.append(
                        {
                            "word": text,
                            "start": word.get("start", 0) + offset,
                            "end": word.get("end", 0) + offset,
                        }
                    )

        if not all_words:
            print(
                "ERROR: No word-level timestamps found in transcript.", file=sys.stderr
            )
            sys.exit(1)

        entries = []
        i = 0
        while i < len(all_words):
            group = all_words[i : i + words_per_line]
            text = " ".join(w["word"] for w in group)
            wrapped = "\n".join(textwrap.wrap(text, width=42))
            entries.append(
                {
                    "start": group[0]["start"],
                    "end": group[-1]["end"],
                    "text": wrapped,
                }
            )
            i += words_per_line

        with open(output_path, "w", encoding="utf-8") as f:
            for idx, entry in enumerate(entries, start=1):
                f.write(f"{idx}\n")
                f.write(
                    f"{Subtitles.ms_to_srt_time(entry['start'])} --> {Subtitles.ms_to_srt_time(entry['end'])}\n"
                )
                f.write(f"{entry['text']}\n\n")

        Utils.log(f"SRT saved: {output_path} ({len(entries)} subtitle entries)", "✅")
