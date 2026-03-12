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
│   ├── merger.py                  ← Merger — merges video, audio, subtitles
│   ├── subtitles.py               ← Subtitles — builds SRT from transcript
│   ├── transcriber.py             ← Transcriber — Whisper transcription
│   ├── tts.py                     ← TTS — text-to-speech with SSML
│   └── videos.py                  ← Video — cuts random segment from source
│
├── features/
│   └── story_background.py        ← StoryBackground — full pipeline as a class
│
├── models/
│   └── api_models.py         ← Models for Requests and Responses (StoryRequest, ClipsRequest, etc.)
│
├── middleware/
│   └── video_generator_middleware.py         ← VideoGeneratorMiddleware — routes requests to the right pipeline
│
├── utils/
│   ├── global_variables.py        ← Variables — all default values
│   └── utils.py                   ← Utils — log, run, get_duration
│
└── main.py                        ← FastAPI entry point
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
pip3 install edge-tts openai-whisper fastapi uvicorn pydantic
```

---

## Adding your source video

Place your long video (e.g. a 30min gameplay clip) at the path defined in `utils/global_variables.py`:

```python
SOURCE_VIDEO = "../videos/source.mp4"
```

The video must be longer than your story's audio — the script picks a random segment each run.

---

## Adding stories

Create `.txt` files inside the `stories/` folder:

```text
stories/1.txt
stories/2.txt
```

Each file should contain plain text — no special formatting needed:

```text
The old lighthouse had been dark for thirty years. Every night, fishermen
would navigate by memory, cursing the broken beacon that once guided them home.
```

---

## How to run

### With Docker (recommended)

```bash
./build-run-docker.sh
```

### Manually

```bash
source .venv/bin/activate
cd src
uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## API

### Submit a job

```bash
curl -X POST "http://localhost:8000/videos" \
  -H "Content-Type: application/json" \
  -d '{"type": "story", "story": "Once upon a time..."}'
```

### Check status

```bash
curl "http://localhost:8000/videos/{job_id}"
```

### Download the result

```bash
curl "http://localhost:8000/videos/{job_id}/download" -o output.mp4
```

### List all jobs

```bash
curl "http://localhost:8000/videos"
```

---

## Request types

### `story`

| Field | Default | Description |
| - | - | - |
| `type` | — | `"story"` |
| `story` | — | Story text |
| `voice` | `en-US-JennyNeural` | TTS voice |
| `model` | `small` | Whisper model size |
| `source` | `/app/videos/source.mp4` | Path to source video |

### `clips` *(coming soon)*

| Field | Default | Description |
| - | - | - |
| `type` | — | `"clips"` |
| `source` | — | Path to the video to split |
| `clip_duration` | `65` | Seconds per clip |

---

## Configuration

Edit defaults in `utils/global_variables.py`:

| Variable | Default | Description |
| - | - | - |
| `SOURCE_VIDEO` | `/app/videos/source.mp4` | Path to source video |
| `WHISPER_MODEL` | `small` | Whisper model size |
| `DEFAULT_VOICE` | `en-US-JennyNeural` | TTS voice |
| `PAD_START` | `0.5` | Seconds of silent video before audio |
| `PAD_END` | `0.5` | Seconds of silent video after audio |
| `OUTPUT_DIR` | `/app/output` | Where final videos are saved |
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
  ✅  Done! Output: /app/output/story_1741234567.mp4
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
| `fastapi` | pip | API framework |
| `uvicorn` | pip | ASGI server |
