#!/usr/bin/env python3
"""
features/clip_generator.py
--------------------------
Takes a video as bytes, transcribes the audio, burns in subtitles,
and splits it into clips of at least 60 seconds — only cutting at
natural sentence boundaries (after . ! ?).
"""

import sys
import tempfile
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from _pipeline.transcriber import Transcriber
from _pipeline.subtitles import Subtitles
from utils.telegram import Telegram
from utils.utils import Utils
from utils.global_variables import Variables


class ClipGenerator:

    def __init__(self, model: str = Variables.WHISPER_MODEL):
        self.model = model
        self.transcriber = Transcriber(model=self.model, language="en")

    async def run(self, video_bytes: bytes, job_id: str = None) -> list[Path]:
        """
        Process a video from raw bytes.
        Returns a list of paths to the generated clips.
        """
        Variables.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)

            # ── Write bytes to a temp file so ffmpeg can read it ──────────
            source_video = tmp / f"{job_id}.mp4"
            source_video.write_bytes(video_bytes)

            # ── Transcribe to get word-level timestamps ───────────────────
            Utils.log("Transcribing video audio...", "📝")
            transcript = self.transcriber.transcribe(source_video)

            # ── Find cut points at sentence boundaries ────────────────────
            cut_points = self._find_cut_points(transcript)
            Utils.log(f"Found {len(cut_points)} cut points", "✂️")

            # ── Cut clips and burn subtitles ──────────────────────────────
            output_files: list[Path] = []
            total = len(cut_points)

            for idx, (start, end) in enumerate(cut_points, start=1):
                clip_num = f"{idx:02d}"
                clip_video = tmp / f"clip_{clip_num}.mp4"
                clip_srt = tmp / f"clip_{clip_num}.srt"
                output_file = Variables.OUTPUT_DIR / f"clip_{job_id}_{clip_num}.mp4"

                # Cut the raw clip
                Utils.run(
                    [
                        "ffmpeg",
                        "-y",
                        "-ss",
                        f"{start:.6f}",
                        "-to",
                        f"{end:.6f}",
                        "-i",
                        str(source_video),
                        "-c",
                        "copy",
                        str(clip_video),
                    ],
                    f"Cutting clip {clip_num} ({start:.1f}s → {end:.1f}s)",
                )

                # Build SRT for this clip — timestamps relative to clip start
                clip_transcript = self._slice_transcript(transcript, start, end)
                Subtitles.build(clip_transcript, clip_srt, offset=-start)

                # Burn subtitles into the clip
                srt_abs = str(clip_srt.resolve()).replace("\\", "/")
                Utils.run(
                    [
                        "ffmpeg",
                        "-y",
                        "-i",
                        str(clip_video),
                        "-vf",
                        f"subtitles='{srt_abs}':force_style='{Variables.SUBTITLE_STYLE}'",
                        "-c:v",
                        "libx264",
                        "-c:a",
                        "aac",
                        "-preset",
                        "fast",
                        "-crf",
                        "23",
                        str(output_file),
                    ],
                    f"Burning subtitles into clip {clip_num}",
                )

                output_files.append(output_file)
                Utils.log(f"Clip {clip_num} saved: {output_file}", "✅")

                await Telegram.send_video(
                    output_file,
                    caption=f"🎬 Clip {clip_num}/{total} — job {job_id}",
                )

            return output_files

    def _find_cut_points(self, transcript: dict) -> list[tuple[float, float]]:
        """
        Walk through all words and find cut points at sentence endings
        (. ! ?) that occur after MIN_CLIP_DURATION seconds from the
        last cut. Never cuts mid-sentence.
        """
        all_words: list[dict] = [
            word
            for segment in transcript.get("segments", [])
            for word in segment.get("words", [])
            if word.get("word", "").strip()
        ]

        if not all_words:
            return []

        total_duration: float = all_words[-1]["end"]
        cut_points: list[tuple[float, float]] = []
        clip_start: float = all_words[0]["start"]

        for word in all_words:
            word_end: float = word.get("end", 0.0)
            word_text: str = word.get("word", "").strip()
            elapsed: float = word_end - clip_start

            # Only consider cutting after MIN_CLIP_DURATION seconds
            # and only at sentence-ending punctuation
            if (
                elapsed >= Variables.MIN_CLIP_DURATION
                and word_text
                and word_text[-1] in ".!?"
            ):
                cut_points.append((clip_start, word_end))
                clip_start = word_end

        # Always include the remainder as the final clip if it has content
        if clip_start < total_duration:
            cut_points.append((clip_start, total_duration))

        return cut_points

    def _slice_transcript(self, transcript: dict, start: float, end: float) -> dict:
        """
        Return a copy of the transcript containing only words
        that fall within [start, end].
        """
        sliced_segments: list[dict] = []

        for segment in transcript.get("segments", []):
            sliced_words: list[dict] = [
                word
                for word in segment.get("words", [])
                if word.get("start", 0.0) >= start and word.get("end", 0.0) <= end
            ]
            if sliced_words:
                sliced_segments.append({**segment, "words": sliced_words})

        return {"segments": sliced_segments}
