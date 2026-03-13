# Video Story Pipeline

Generates short videos from a text story. It picks a random segment from a long source video, converts the story to speech, transcribes it into subtitles, burns a title in the centre of the video, and saves everything as a final `.mp4`.

---

## What the pipeline does

1. Reads your story title and text
2. Generates a voiceover using `edge-tts` — title spoken first, followed by a pause, then the story
3. Prepends 0.1s of silence to the audio for a clean lead-in
4. Transcribes the audio with Whisper to get word-level timestamps
5. Builds an `.srt` subtitle file from the transcript
6. Cuts a random segment from your source video — same length as the audio plus a silent tail
7. Burns the subtitles and the title (centred, permanent) into the video
8. Merges the audio and sends the result to Telegram
9. Saves the final `.mp4` to the `output/` folder

---

## Project structure

```text
src/
│
├── _pipeline/                          ← reusable pipeline modules
│   ├── merger.py                       ← Merger — merges video, audio, subtitles, title
│   ├── subtitles.py                    ← Subtitles — builds SRT from transcript
│   ├── transcriber.py                  ← Transcriber — Whisper transcription
│   ├── tts.py                          ← TTS — text-to-speech via edge-tts
│   └── videos.py                       ← Video — cuts random segment from source
│
├── features/
│   └── story_background.py             ← StoryBackground — full pipeline as a class
│
├── infrastructure/
│   ├── piper_voice.py                  ← PiperVoice enum (unused if using edge-tts)
│   └── voice_downloader.py             ← VoiceDownloader — downloads Piper models at startup
│
├── middleware/
│   └── video_generator_middleware.py   ← routes requests to the right pipeline
│
├── models/
│   └── api_models.py                   ← StoryRequest, ClipsRequest, JobResponse, etc.
│
├── utils/
│   ├── global_variables.py             ← Variables — all default config values
│   ├── telegram.py                     ← Telegram — sends video to channel
│   └── utils.py                        ← Utils — log, run, get_duration, generate_job_id
│
└── main.py                             ← FastAPI entry point
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
pip3 install edge-tts openai-whisper fastapi uvicorn pydantic httpx python-dotenv python-multipart
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHANNEL_ID=-1001234567890
```

---

## Adding your source video

Place your long video at the path defined in `utils/global_variables.py`:

```python
SOURCE_VIDEO = "../videos/source.mp4"
```

The video must be longer than your story's audio — the script picks a random segment each run.

---

## How to run

### With Docker (recommended)

```bash
./build-run-docker.sh        # Linux / Mac
./build-run-docker.ps1       # Windows (PowerShell)
```

### Manually

```bash
source .venv/bin/activate
cd src
uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## API

### Submit a story job

```bash
curl -X POST "http://localhost:8000/generate-video" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "The Lighthouse",
    "story": "The old lighthouse had been dark for thirty years..."
  }'
```

### Check status

```bash
curl "http://localhost:8000/status/{job_id}"
```

### Download the result

```bash
curl "http://localhost:8000/download/{job_id}" -o output.mp4
```

### List all jobs

```bash
curl "http://localhost:8000/jobs"
```

---

## Request fields

### `StoryRequest`

| Field | Required | Default | Description |
| - | - | - | - |
| `title` | ✅ | — | Title spoken at the start and shown centred on video |
| `story` | ✅ | — | Story text for the voiceover |
| `voice` | — | `en-US-AriaNeural` | edge-tts voice name |
| `model` | — | `small` | Whisper model size |
| `source` | — | `/app/videos/source.mp4` | Path to source video |

---

## Configuration

Edit defaults in `utils/global_variables.py`:

| Variable | Default | Description |
| - | - | - |
| `SOURCE_VIDEO` | `/app/videos/source.mp4` | Path to source video |
| `WHISPER_MODEL` | `small` | Whisper model size |
| `DEFAULT_VOICE` | `en-US-AriaNeural` | TTS voice |
| `PAD_END` | `0.5` | Seconds of silent video after audio |
| `TTS_PAD_START` | `0.1` | Seconds of silence prepended to TTS audio |
| `TTS_RATE` | `+0%` | edge-tts speech rate |
| `TTS_PITCH` | `+0Hz` | edge-tts pitch adjustment |
| `OUTPUT_DIR` | `/app/output` | Where final videos are saved |
| `SUBTITLE_STYLE` | Arial 22px white | ffmpeg subtitle style string |
| `MIN_CLIP_DURATION` | `60` | Minimum clip length in seconds (clip pipeline) |

---

## Pipeline classes

| File | Class | Type | Responsibility |
| - | - | - | - |
| `tts.py` | `TTS` | Instance | Generates speech from title + story text |
| `transcriber.py` | `Transcriber` | Instance | Transcribes audio with Whisper |
| `subtitles.py` | `Subtitles` | Static | Builds `.srt` from transcript |
| `videos.py` | `Video` | Instance | Cuts random segment from source video |
| `merger.py` | `Merger` | Instance | Merges video + audio + subtitles + title overlay |

**Static** classes (`Utils`, `Subtitles`) are pure functions with no state.
**Instance** classes (`TTS`, `Transcriber`, `Video`, `Merger`) are configured once at init and reused.

---

## TTS behaviour

- Title is spoken first, followed by a `...` pause, then the story
- Short pauses are inserted after `.!?` sentence endings
- 0.1s of silence is prepended to the audio for a clean lead-in (`TTS_PAD_START`)
- No SSML — edge-tts uses plain text with `rate` and `pitch` parameters

---

## Whisper model sizes

| Model | Size | Speed on CPU | Quality |
| - | - | - | - |
| `tiny` | ~74MB | Fast | Rough |
| `base` | ~74MB | Fast | OK |
| `small` | ~244MB | Moderate | **Good (default)** |
| `medium` | ~769MB | Slow | Better |
| `large-v3` | ~1.5GB | Very slow | Best |

On a CPU-only machine or inside Docker on Mac, `small` is the recommended balance. Use `base` if speed matters more than accuracy. Note that Docker on Mac has no GPU access — run outside Docker for faster Whisper inference on Apple Silicon.

---

## Dependencies

| Tool | Type | Purpose |
| - | - | - |
| `ffmpeg` | system (`apt`) | Video cutting, encoding, subtitle burn-in, drawtext |
| `ffprobe` | system (`apt`) | Reading video/audio duration |
| `fonts-dejavu-core` | system (`apt`) | Font for title overlay via drawtext |
| `edge-tts` | pip | Text-to-speech, free, no API key needed |
| `openai-whisper` | pip | Local audio transcription |
| `whisper-ctranslate2` | pip (optional) | Faster transcription on CPU |
| `fastapi` | pip | API framework |
| `uvicorn` | pip | ASGI server |
| `httpx` | pip | Async HTTP client for Telegram |
| `python-dotenv` | pip | Loads `.env` file at startup |
| `python-multipart` | pip | Multipart file upload support |
