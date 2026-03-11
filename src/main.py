#!/usr/bin/env python3
"""
_api/main.py
------
FastAPI wrapper for the Video Story Pipeline.

Endpoints:
    POST /generate        — submit a story, get a job_id back
    GET  /status/{job_id} — check job status
    GET  /download/{job_id} — download the finished video

Usage:
    uvicorn api:app --host 0.0.0.0 --port 8000 --reload

Example:
    curl -X POST "http://localhost:8000/generate" \
         -H "Content-Type: application/json" \
         -d '{"story": "Once upon a time..."}'
"""

import sys
import tempfile
import time
import uuid
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

sys.path.append(str(Path(__file__).resolve().parent))

from _pipeline.tts import TTS
from _pipeline.transcriber import Transcriber
from _pipeline.subtitles import Subtitles
from _pipeline.videos import Video
from _pipeline.merger import Merger
from utils.utils import Utils
from utils.global_variables import Variables

# ── App ───────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Video Story Pipeline API",
    description="Generate story videos with TTS audio and burned-in subtitles.",
    version="1.0.0",
)

# ── In-memory job store ───────────────────────────────────────────────────────
# For production, replace with Redis or a database

jobs: dict = {}

# ── Request / Response models ─────────────────────────────────────────────────


class GenerateRequest(BaseModel):
    story: str
    voice: str = Variables.DEFAULT_VOICE
    model: str = Variables.WHISPER_MODEL
    source: str = Variables.SOURCE_VIDEO


class JobResponse(BaseModel):
    job_id: str
    status: str
    message: str


class StatusResponse(BaseModel):
    job_id: str
    status: str  # pending | running | done | error
    output: Optional[str] = None
    error: Optional[str] = None
    duration: Optional[float] = None


# ── Pipeline runner ───────────────────────────────────────────────────────────


async def run_pipeline(job_id: str, request: GenerateRequest):
    """Run the full pipeline and update job status."""
    jobs[job_id]["status"] = "running"
    start = time.time()

    try:
        source = Path(request.source)
        if not source.exists():
            raise FileNotFoundError(f"Source video not found: {source}")

        Variables.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        tts = TTS(voice=request.voice)
        transcriber = Transcriber(model=request.model, language="en")
        video = Video(pad_start=Variables.PAD_START, pad_end=Variables.PAD_END)
        merger = Merger(
            pad_start=Variables.PAD_START, subtitle_style=Variables.SUBTITLE_STYLE
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            tts_audio = tmp / "tts_audio.mp3"
            cut_vid = tmp / "cut_video.mp4"
            srt_file = tmp / "subtitles.srt"
            output_file = Variables.OUTPUT_DIR / f"story_{job_id}.mp4"

            await tts.generate(request.story, tts_audio)

            audio_duration = Utils.get_duration(tts_audio)
            transcript = transcriber.transcribe(tts_audio)

            Subtitles.build(transcript, srt_file, offset=Variables.PAD_START)
            video.cut_segment(source, audio_duration, cut_vid)
            merger.merge(cut_vid, tts_audio, srt_file, output_file)

        jobs[job_id]["status"] = "done"
        jobs[job_id]["output"] = str(output_file.resolve())
        jobs[job_id]["duration"] = round(time.time() - start, 2)

    except Exception as e:
        jobs[job_id]["status"] = "error"
        jobs[job_id]["error"] = str(e)


# ── Routes ────────────────────────────────────────────────────────────────────


@app.get("/")
def root():
    return {"status": "ok", "message": "Video Story Pipeline API is running"}


@app.post("/generate", response_model=JobResponse, status_code=202)
async def generate(request: GenerateRequest, background_tasks: BackgroundTasks):
    """
    Submit a story for video generation.
    Returns a job_id immediately — generation runs in the background.
    """
    if not request.story.strip():
        raise HTTPException(status_code=400, detail="Story text cannot be empty")

    job_id = str(uuid.uuid4())[:8]
    jobs[job_id] = {
        "status": "pending",
        "output": None,
        "error": None,
        "duration": None,
    }

    background_tasks.add_task(run_pipeline, job_id, request)

    return JobResponse(
        job_id=job_id,
        status="pending",
        message=f"Job accepted. Poll /status/{job_id} to check progress.",
    )


@app.get("/status/{job_id}", response_model=StatusResponse)
def status(job_id: str):
    """Check the status of a generation job."""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs[job_id]
    return StatusResponse(
        job_id=job_id,
        status=job["status"],
        output=job["output"],
        error=job["error"],
        duration=job["duration"],
    )


@app.get("/download/{job_id}")
def download(job_id: str):
    """Download the finished video for a completed job."""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs[job_id]

    if job["status"] != "done":
        raise HTTPException(
            status_code=400, detail=f"Job is not done yet — status: {job['status']}"
        )

    output_path = Path(job["output"])
    if not output_path.exists():
        raise HTTPException(status_code=404, detail="Output file not found")

    return FileResponse(
        path=output_path,
        media_type="video/mp4",
        filename=output_path.name,
    )


@app.get("/jobs")
def list_jobs():
    """List all jobs and their statuses."""
    return {
        "total": len(jobs),
        "jobs": [
            {"job_id": jid, "status": j["status"], "duration": j["duration"]}
            for jid, j in jobs.items()
        ],
    }
