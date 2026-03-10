#!/usr/bin/env python3
"""
Video Story Pipeline
--------------------
Receives a story text, cuts a random segment from a single long video,
generates TTS audio, transcribes it to build SRT subtitles,
and burns everything into a final output video.

The video cut is:
  - Same duration as the TTS audio + 1 second total padding
  - 0.5s extra video before the cut start
  - 0.5s extra video after the cut end
  - Cut is done as a stream copy (fast, no re-encoding)

Usage:
    python3 video_story_pipeline.py --story "Your story text here"
    python3 video_story_pipeline.py --story-file story.txt
    python3 video_story_pipeline.py --story "Your story" --voice en-US-GuyNeural
    python3 video_story_pipeline.py --source /path/to/long_video.mp4 --story "..."
    python3 video_story_pipeline.py --list-voices
"""

import argparse
import asyncio
import json
import random
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path

# ── Configuration ─────────────────────────────────────────────────────────────

SOURCE_VIDEO = "./videos/minecraft-parkour.mp4"

PAD_START = 0.5
PAD_END = 0.5

OUTPUT_DIR = Path("./output")

WHISPER_MODEL = "small"

DEFAULT_VOICE = "en-US-AriaNeural"

SUBTITLE_STYLE = (
    "FontSize=22,"
    "FontName=Arial,"
    "Bold=1,"
    "PrimaryColour=&H00FFFFFF,"
    "OutlineColour=&H00000000,"
    "Outline=2,"
    "Shadow=1,"
    "Alignment=2,"
    "MarginV=40"
)

# ── Helpers ───────────────────────────────────────────────────────────────────


def log(msg: str, emoji: str = "▶"):
    print(f"\n{emoji}  {msg}", flush=True)


def run(cmd: list, desc: str = "") -> subprocess.CompletedProcess:
    if desc:
        log(desc, "⚙")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ERROR: {result.stderr.strip()}", file=sys.stderr)
        sys.exit(1)
    return result


def get_duration(path: Path) -> float:
    result = run(
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


# ── Step 1: Generate TTS audio ────────────────────────────────────────────────


async def generate_tts(story: str, voice: str, output_path: Path):
    import edge_tts

    log(f"Generating TTS with voice: {voice}", "🗣")
    communicate = edge_tts.Communicate(story, voice)
    await communicate.save(str(output_path))
    log(f"TTS audio saved: {output_path}", "✅")


# ── Step 2: Transcribe audio ──────────────────────────────────────────────────


def transcribe_audio(audio_path: Path, model: str) -> dict:
    log(f"Transcribing audio with Whisper ({model} model)...", "📝")

    whisper_cmd = None
    for cmd in ["whisper-ctranslate2", "whisper"]:
        result = subprocess.run(["which", cmd], capture_output=True)
        if result.returncode == 0:
            whisper_cmd = cmd
            break

    if not whisper_cmd:
        print("ERROR: Neither whisper nor whisper-ctranslate2 found.", file=sys.stderr)
        sys.exit(1)

    log(f"Using: {whisper_cmd}", "🔍")

    with tempfile.TemporaryDirectory() as tmpdir:
        run(
            [
                whisper_cmd,
                str(audio_path),
                "--model",
                model,
                "--output_format",
                "json",
                "--word_timestamps",
                "true",
                "--language",
                "en",
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


# ── Step 3: Build SRT ─────────────────────────────────────────────────────────


def ms_to_srt_time(seconds: float) -> str:
    ms = int((seconds % 1) * 1000)
    s = int(seconds) % 60
    m = int(seconds // 60) % 60
    h = int(seconds // 3600)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def build_srt(
    transcript: dict, output_path: Path, offset: float = 0.0, words_per_line: int = 8
):
    log("Building SRT subtitle file", "📄")

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
        print("ERROR: No word-level timestamps found in transcript.", file=sys.stderr)
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
                f"{ms_to_srt_time(entry['start'])} --> {ms_to_srt_time(entry['end'])}\n"
            )
            f.write(f"{entry['text']}\n\n")

    log(f"SRT saved: {output_path} ({len(entries)} subtitle entries)", "✅")


# ── Step 4: Cut video segment ─────────────────────────────────────────────────


def cut_video_segment(source: Path, audio_duration: float, output_path: Path) -> None:
    source_duration = get_duration(source)
    clip_duration = audio_duration + PAD_START + PAD_END

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

    log(
        f"Random cut: {cut_start:.2f}s → {cut_end:.2f}s  "
        f"| clip: {clip_duration:.2f}s  "
        f"| audio: {audio_duration:.2f}s  "
        f"| padding: +{PAD_START}s / +{PAD_END}s",
        "✂️",
    )

    run(
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

    log(f"Video segment saved: {output_path}", "✅")


# ── Step 5: Merge final video ─────────────────────────────────────────────────


def merge_final(video_path: Path, audio_path: Path, srt_path: Path, output_path: Path):
    log("Merging video + audio + subtitles into final output", "🎞")

    srt_abs = str(srt_path.resolve()).replace("\\", "/")
    adelay_ms = int(PAD_START * 1000)

    run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(video_path),
            "-i",
            str(audio_path),
            "-filter_complex",
            (
                f"[0:v]subtitles='{srt_abs}':force_style='{SUBTITLE_STYLE}'[v];"
                f"[1:a]adelay={adelay_ms}|{adelay_ms}[a]"
            ),
            "-map",
            "[v]",
            "-map",
            "[a]",
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

    log(f"Final video saved: {output_path}", "🎉")


# ── Main ──────────────────────────────────────────────────────────────────────


def list_voices():
    result = subprocess.run(
        ["edge-tts", "--list-voices"], capture_output=True, text=True
    )
    print(result.stdout)


async def run_pipeline(story: str, voice: str, model: str, source_video: str):
    source = Path(source_video)
    if not source.exists():
        print(f"ERROR: Source video not found: {source.resolve()}", file=sys.stderr)
        sys.exit(1)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)

        tts_audio = tmp / "tts_audio.mp3"
        cut_vid = tmp / "cut_video.mp4"
        srt_file = tmp / "subtitles.srt"

        import time

        output_file = OUTPUT_DIR / f"story_{int(time.time())}.mp4"

        await generate_tts(story, voice, tts_audio)

        audio_duration = get_duration(tts_audio)
        log(f"Audio duration: {audio_duration:.2f}s", "🎵")

        transcript = transcribe_audio(tts_audio, model)
        build_srt(transcript, srt_file, offset=PAD_START)
        cut_video_segment(source, audio_duration, cut_vid)
        merge_final(cut_vid, tts_audio, srt_file, output_file)

        total = audio_duration + PAD_START + PAD_END
        print(f"\n{'─'*52}")
        print(f"  ✅  Done! Output: {output_file.resolve()}")
        print(f"  🎬  Total video:  {total:.2f}s")
        print(f"  ⏱   Lead-in:      0s → {PAD_START}s  (silent)")
        print(f"  🎵  Audio+subs:   {PAD_START}s → {PAD_START + audio_duration:.2f}s")
        print(
            f"  ⏱   Tail:         {PAD_START + audio_duration:.2f}s → {total:.2f}s  (silent)"
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
        default=DEFAULT_VOICE,
        help=f"edge-tts voice name (default: {DEFAULT_VOICE})",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=WHISPER_MODEL,
        help=f"Whisper model size (default: {WHISPER_MODEL})",
    )
    parser.add_argument(
        "--source",
        type=str,
        default=SOURCE_VIDEO,
        help=f"Path to source video (default: {SOURCE_VIDEO})",
    )
    parser.add_argument(
        "--list-voices", action="store_true", help="List available TTS voices and exit"
    )

    args = parser.parse_args()

    if args.list_voices:
        list_voices()
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
