#!/usr/bin/env python3
"""
main.py
-------
FastAPI wrapper for the Video Story Pipeline.

Endpoints:
    POST /generate          — submit a story, get a job_id back
    GET  /status/{job_id}   — check job status
    GET  /download/{job_id} — download the finished video
    GET  /jobs              — list all jobs

Usage:
    uvicorn main:app --host 0.0.0.0 --port 8000

Example:
    curl -X POST "http://localhost:8000/generate" \
         -H "Content-Type: application/json" \
         -d '{"story": "Once upon a time..."}'
"""

import uuid
from pathlib import Path
from typing import Union

from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from models.api_models import (
    ClipsRequest,
    GenerateRequest,
    JobResponse,
    StatusResponse,
    StoryRequest,
)

from middleware.video_generator_middleware import VideoGeneratorMiddleware

# ── App ───────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Video Story Pipeline API",
    description="Generate story videos with TTS audio and burned-in subtitles.",
    version="1.0.0",
)

# ── In-memory job store ───────────────────────────────────────────────────────

jobs: dict = {}


# ── Pipeline runner ───────────────────────────────────────────────────────────


async def run_pipeline(job_id: str, request):
    middleware = VideoGeneratorMiddleware(jobs)
    await middleware.run(job_id, request)


# ── Routes ────────────────────────────────────────────────────────────────────


@app.get("/")
def root():
    return {"status": "ok", "message": "Video Story Pipeline API is running"}


@app.post("/videos", response_model=JobResponse, status_code=202)
async def generate(
    request: Union[StoryRequest, ClipsRequest], background_tasks: BackgroundTasks
):
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

    return StatusResponse(job_id=job_id, **job)


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
        path=output_path, media_type="video/mp4", filename=output_path.name
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
