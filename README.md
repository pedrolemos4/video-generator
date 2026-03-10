# Video Story Pipeline

Generates short videos from a text story. It picks a random segment from a long source video, converts the story to speech, transcribes it into subtitles, and burns everything into a final `.mp4`.

---

## What the script does

1. Reads your story text
2. Generates a voiceover from it using `edge-tts` with SSML for expressive, human-sounding speech
3. Transcribes the audio with Whisper to get word-level timestamps
4. Builds an `.srt` subtitle file from the transcript
5. Cuts a random segment from your source video — same length as the audio, plus 0.5s of silent video before and after
6. Burns the subtitles into the video and merges the audio
7. Saves the final `.mp4` to the `output/` folder

---

## Project structure

```text
src/
│
├── _pipeline/                     ← reusable pipeline modules
│   ├── merger.py                  ← Merger  — merges video, audio, subtitles
│   ├── subtitles.py               ← Subtitles — builds SRT from transcript
│   ├── transcriber.py             ← Transcriber — Whisper transcription
│   ├── tts.py                     ← TTS — text-to-speech with SSML
│   └── videos.py                  ← Video — cuts random segment from source
│
├── story-background/              ← this project
│   └── main.py                    ← entry point
│
└── utils/
    ├── global_variables.py        ← Config — all default values
    └── utils.py                   ← Utils — log, run, get_duration
```

---

## Setup

### 1. Install system dependencies

```bash
sudo bash install_dependencies.sh
```

### 2. Create and activate virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Python packages

```bash
pip install edge-tts openai-whisper
```

---

## Adding your source video

Place your long video (e.g. a 30min gameplay clip) at the path defined in `utils/global_variables.py`:

```python
SOURCE_VIDEO = "../../videos/source.mp4"
```

Or pass a different path at runtime using `--source`. The video must be longer than your story's audio — the script picks a random segment each run.

---

## Adding stories

Create `.txt` files anywhere and point to them with `--story-file`:

```text
src/story-background/stories/1.txt
src/story-background/stories/2.txt
```

Each file should contain plain text — no special formatting needed:

```text
The old lighthouse had been dark for thirty years. Every night, fishermen
would navigate by memory, cursing the broken beacon that once guided them home.
```

---

## How to run

Activate the virtual environment first:

```bash
source .venv/bin/activate
```

```bash
python3 main.py --story-file stories/1.txt
python3 main.py --story "Once upon a time..."
python3 main.py --story-file stories/1.txt --voice en-US-GuyNeural
python3 main.py --story-file stories/1.txt --source /path/to/video.mp4
python3 main.py --story-file stories/1.txt --model base
python3 main.py --list-voices
```

---

## Configuration

Edit defaults in `utils/global_variables.py`:

| Variable | Default | Description |
| - | - | - |
| `SOURCE_VIDEO` | `../../videos/source.mp4` | Path to source video |
| `WHISPER_MODEL` | `small` | Whisper model size |
| `DEFAULT_VOICE` | `en-US-JennyNeural` | TTS voice |
| `PAD_START` | `0.5` | Seconds of silent video before audio |
| `PAD_END` | `0.5` | Seconds of silent video after audio |
| `OUTPUT_DIR` | `../../output` | Where final videos are saved |
| `SUBTITLE_STYLE` | Arial 22px white | ffmpeg subtitle style string |

---

## Pipeline classes

Each module in `_pipeline/` is independently reusable in other projects:

| File | Class | Type | Responsibility |
| - | - | - | - |
| `tts.py` | `TTS` | Instance | Generates speech from text using SSML |
| `transcriber.py` | `Transcriber` | Instance | Transcribes audio with Whisper |
| `subtitles.py` | `Subtitles` | Static | Builds `.srt` from transcript |
| `videos.py` | `Video` | Instance | Cuts random segment from source video |
| `merger.py` | `Merger` | Instance | Merges video + audio + subtitles |

**Static** classes (`Utils`, `Subtitles`) are pure functions with no state.
**Instance** classes (`TTS`, `Transcriber`, `Video`, `Merger`) are configured once at init and reused.

---

## Whisper model sizes

| Model | Size | Speed on Pi | Quality |
| - | - | - | - |
| `tiny` | ~74MB | Fast | Rough |
| `base` | ~74MB | Fast | OK |
| `small` | ~244MB | Moderate | **Good (default)** |
| `medium` | ~769MB | Slow | Better |
| `large-v3` | ~1.5GB | Very slow | Best |

On a Raspberry Pi or CPU-only machine, `small` is the recommended balance. Use `base` if speed matters more than accuracy.

---

## Output

Each run saves a timestamped file to `output/`:

```text
output/story_1741234567.mp4
```

The terminal prints a summary when done:

```text
────────────────────────────────────────────────────
  ✅  Done! Output: /home/pedro/video-generator/output/story_1741234567.mp4
  🎬  Total video:  35.50s
  ⏱   Lead-in:      0s → 0.5s  (silent)
  🎵  Audio+subs:   0.5s → 35.0s
  ⏱   Tail:         35.0s → 35.5s  (silent)
────────────────────────────────────────────────────
```

---

## Dependencies

| Tool | Type | Purpose |
| - | - | - |
| `ffmpeg` | system (`apt`) | Video cutting, encoding, subtitle burn-in |
| `ffprobe` | system (`apt`) | Reading video/audio duration |
| `edge-tts` | pip | Text-to-speech, free, no API key needed |
| `openai-whisper` | pip | Local audio transcription |
| `whisper-ctranslate2` | pip (optional) | Faster transcription on CPU |
