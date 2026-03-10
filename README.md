# Video Story Pipeline

Generates short videos from a text story. It picks a random segment from a long source video, converts the story to speech, transcribes it into subtitles, and burns everything into a final `.mp4`.

---

## What the script does

1. Reads your story text
2. Generates a voiceover from it using `edge-tts`
3. Transcribes the audio with Whisper to get word-level timestamps
4. Builds an `.srt` subtitle file from the transcript
5. Cuts a random segment from your source video — same length as the audio, plus 0.5s of silent video before and after
6. Burns the subtitles into the video and merges the audio
7. Saves the final `.mp4` to the `output/` folder

---

## Project structure

```text
video-generator/
│
├── video_story_pipeline.py   ← main script
│
├── videos/
│   └── source.mp4            ← your long source video goes here
│
├── stories/
│   ├── 1.txt                 ← story files go here
│   ├── 2.txt
│   └── ...
│
└── output/                   ← generated videos are saved here (auto-created)
    └── story_1234567890.mp4
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

Place your long video (e.g. a 30min gameplay clip) at:

```text
videos/source.mp4
```

Or point to a different path using the `--source` flag at runtime, or by editing `SOURCE_VIDEO` at the top of the script:

```python
SOURCE_VIDEO = "./videos/source.mp4"
```

The video must be longer than your story's audio. The script will pick a random segment from it each time it runs.

---

## Adding stories

Create `.txt` files inside the `stories/` folder:

```text
stories/1.txt
stories/2.txt
stories/my-story.txt
```

Each file should contain plain text — just write the story, no special formatting needed. Example:

```text
The old lighthouse had been dark for thirty years. Every night, fishermen
would navigate by memory, cursing the broken beacon that once guided them home.
```

---

## How to run

Make sure the virtual environment is active first:

```bash
source .venv/bin/activate
```

**From a story file:**

```bash
python video_story_pipeline.py --story-file stories/1.txt
```

**From a string directly:**

```bash
python video_story_pipeline.py --story "Once upon a time..."
```

**With a custom voice:**

```bash
python video_story_pipeline.py --story-file stories/1.txt --voice en-US-GuyNeural
```

**With a different source video:**

```bash
python video_story_pipeline.py --story-file stories/1.txt --source videos/other.mp4
```

**With a different Whisper model:**

```bash
python video_story_pipeline.py --story-file stories/1.txt --model base
```

**List all available voices:**

```bash
python video_story_pipeline.py --list-voices
```

---

## Configuration (top of script)

You can change these defaults directly in `video_story_pipeline.py`:

| Variable | Default | Description |
| -------- | ------- | ----------- |
| `SOURCE_VIDEO` | `./videos/source.mp4` | Path to source video |
| `WHISPER_MODEL` | `small` | Whisper model size |
| `DEFAULT_VOICE` | `en-US-AriaNeural` | TTS voice |
| `PAD_START` | `0.5` | Seconds of silent video before audio |
| `PAD_END` | `0.5` | Seconds of silent video after audio |
| `OUTPUT_DIR` | `./output` | Where final videos are saved |

---

## Whisper model sizes

| Model | Size | Speed on Pi | Quality |
| ----- | ---- | ----------- | ------- |
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

The terminal will print a summary when done:

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
| ---- | ---- | ------- |
| `ffmpeg` | system (`apt`) | Video cutting, encoding, subtitle burn-in |
| `ffprobe` | system (`apt`) | Reading video/audio duration |
| `edge-tts` | pip | Text-to-speech (free, no API key) |
| `openai-whisper` | pip | Local audio transcription |
| `whisper-ctranslate2` | pip (optional) | Faster transcription on CPU |
