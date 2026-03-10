#!/usr/bin/env python3
"""
story-background/main.py
------------------------
Entry point for the Story Background video pipeline.

Usage:
    python3 main.py --story "Your story text here"
    python3 main.py --story-file stories/1.txt
    python3 main.py --story-file stories/1.txt --voice en-US-GuyNeural
    python3 main.py --story-file stories/1.txt --source /path/to/video.mp4
    python3 main.py --list-voices
"""

import argparse
import asyncio
import sys
import tempfile
import time
from pathlib import Path

# Add src root to path so pipeline/ and utils/ are importable
sys.path.append(str(Path(__file__).resolve().parent.parent))

from _pipeline.tts import TTS
from _pipeline.transcriber import Transcriber
from _pipeline.subtitles import Subtitles
from _pipeline.videos import Video
from _pipeline.merger import Merger
from utils.utils import Utils
from utils.global_variables import Variables


async def run_pipeline(story: str, voice: str, model: str, source_video: str):
    source = Path(source_video)
    if not source.exists():
        print(f"ERROR: Source video not found: {source.resolve()}", file=sys.stderr)
        sys.exit(1)

    Variables.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # ── Instantiate pipeline classes with project config ───────────────────
    tts = TTS(voice=voice)
    transcriber = Transcriber(model=model, language="en")
    video = Video(pad_start=Variables.PAD_START, pad_end=Variables.PAD_END)
    merger = Merger(
        pad_start=Variables.PAD_START, subtitle_style=Variables.SUBTITLE_STYLE
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        tts_audio = tmp / "tts_audio.mp3"
        cut_vid = tmp / "cut_video.mp4"
        srt_file = tmp / "subtitles.srt"
        output_file = Variables.OUTPUT_DIR / f"story_{int(time.time())}.mp4"

        # ── Pipeline ──────────────────────────────────────────────────────
        await tts.generate(story, tts_audio)

        audio_duration = Utils.get_duration(tts_audio)
        Utils.log(f"Audio duration: {audio_duration:.2f}s", "🎵")

        transcript = transcriber.transcribe(tts_audio)
        Subtitles.build(transcript, srt_file, offset=Variables.PAD_START)
        video.cut_segment(source, audio_duration, cut_vid)
        merger.merge(cut_vid, tts_audio, srt_file, output_file)

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


def main():
    parser = argparse.ArgumentParser(
        description="Generate a story video with TTS audio and burned-in subtitles."
    )
    parser.add_argument("--story", type=str, help="Story text as a string")
    parser.add_argument(
        "--story-file", type=str, help="Path to a .txt file with the story"
    )
    parser.add_argument(
        "--voice",
        type=str,
        default=Variables.DEFAULT_VOICE,
        help=f"edge-tts voice (default: {Variables.DEFAULT_VOICE})",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=Variables.WHISPER_MODEL,
        help=f"Whisper model size (default: {Variables.WHISPER_MODEL})",
    )
    parser.add_argument(
        "--source",
        type=str,
        default=Variables.SOURCE_VIDEO,
        help=f"Path to source video (default: {Variables.SOURCE_VIDEO})",
    )
    parser.add_argument(
        "--list-voices", action="store_true", help="List available TTS voices and exit"
    )

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

    asyncio.run(run_pipeline(story, args.voice, args.model, args.source))


if __name__ == "__main__":
    main()
