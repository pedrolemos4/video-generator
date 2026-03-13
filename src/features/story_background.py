#!/usr/bin/env python3
"""
features/story_background.py
-----------------------------
Takes in a story as text, generates TTS audio, creates subtitles, and merges with a source video to produce a final output.
Can be used as a class from main.py or run directly from the CLI.

CLI Usage:
    python3 story_background.py --story "Your story text here"
    python3 story_background.py --story-file stories/1.txt
    python3 story_background.py --list-voices
"""

import argparse
import asyncio
import sys
import tempfile
import time
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from _pipeline.tts import TTS
from _pipeline.transcriber import Transcriber
from _pipeline.subtitles import Subtitles
from _pipeline.videos import Video
from _pipeline.merger import Merger
from utils.utils import Utils
from utils.global_variables import Variables
from utils.telegram import Telegram


class StoryBackground:

    def __init__(
        self,
        voice: str = Variables.DEFAULT_VOICE,
        model: str = Variables.WHISPER_MODEL,
        source_video: str = Variables.SOURCE_VIDEO,
    ):
        self.voice = voice
        self.model = model
        self.source = Path(source_video)

        self.tts = TTS(voice=self.voice)
        self.transcriber = Transcriber(model=self.model, language="en")
        self.video = Video(pad_start=Variables.PAD_START, pad_end=Variables.PAD_END)
        self.merger = Merger(
            pad_start=Variables.PAD_START, subtitle_style=Variables.SUBTITLE_STYLE
        )

    async def run(self, story: str, job_id: str = None) -> Path:
        """
        Run the full pipeline for a given story.
        Returns the path to the generated video.
        """
        if not self.source.exists():
            print(
                f"ERROR: Source video not found: {self.source.resolve()}",
                file=sys.stderr,
            )
            raise FileNotFoundError(f"Source video not found: {self.source}")

        Variables.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        filename = f"story_{job_id}.mp4" if job_id else f"story_{int(time.time())}.mp4"

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            tts_audio = tmp / f"{job_id}_tts_audio.mp3"
            cut_vid = tmp / f"{job_id}_cut_video.mp4"
            srt_file = tmp / f"{job_id}_subtitles.srt"
            output_file = Variables.OUTPUT_DIR / filename

            await self.tts.generate(story, tts_audio)

            audio_duration = Utils.get_duration(tts_audio)
            Utils.log(f"Audio duration: {audio_duration:.2f}s", "🎵")

            transcript = self.transcriber.transcribe(tts_audio)
            Subtitles.build(transcript, srt_file, offset=Variables.PAD_START)
            self.video.cut_segment(self.source, audio_duration, cut_vid)
            self.merger.merge(cut_vid, tts_audio, srt_file, output_file)

            await Telegram.send_video(
                output_file, caption=f"✅ Story ready — job {job_id}"
            )

            total = audio_duration + Variables.PAD_START + Variables.PAD_END
            print(f"\n{'─'*52}")
            print(f"  ✅  Done! Output: {output_file.resolve()}")
            print(f"  🎬  Total video:  {total:.2f}s")
            print(f"  ⏱   Lead-in:      0s → {Variables.PAD_START}s  (silent)")
            print(
                f"  🎵  Audio+subs:   {Variables.PAD_START}s → {Variables.PAD_START + audio_duration:.2f}s"
            )
            print(
                f"  ⏱   Tail:         {Variables.PAD_START + audio_duration:.2f}s → {total:.2f}s  (silent)"
            )
            print(f"{'─'*52}\n")

            return output_file


# ── CLI entry point ───────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(
        description="Generate a story video with TTS audio and burned-in subtitles."
    )
    parser.add_argument("--story", type=str, help="Story text as a string")
    parser.add_argument(
        "--story-file", type=str, help="Path to a .txt file with the story"
    )
    parser.add_argument("--voice", type=str, default=Variables.DEFAULT_VOICE)
    parser.add_argument("--model", type=str, default=Variables.WHISPER_MODEL)
    parser.add_argument("--source", type=str, default=Variables.SOURCE_VIDEO)
    parser.add_argument("--list-voices", action="store_true")

    args = parser.parse_args()

    if args.list_voices:
        TTS.list_voices()
        sys.exit(0)

    if args.story_file:
        with open(args.story_file, "r") as f:
            story = f.read().strip()
    elif args.story:
        story = args.story.strip()
    else:
        parser.print_help()
        sys.exit(1)

    if not story:
        print("ERROR: Story text is empty.", file=sys.stderr)
        sys.exit(1)

    pipeline = StoryBackground(
        voice=args.voice, model=args.model, source_video=args.source
    )
    asyncio.run(pipeline.run(story))


if __name__ == "__main__":
    main()
