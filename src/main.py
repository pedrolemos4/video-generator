#!/usr/bin/env python3
"""
main.py
-------
FastAPI wrapper for the Video Story Pipeline.

Endpoints:
    POST /videos          — submit a story, get a job_id back
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

from pathlib import Path
from typing import Union

from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from models.api_models import (
    ClipsRequest,
    JobResponse,
    StatusResponse,
    StoryRequest,
)

from middleware.video_generator_middleware import VideoGeneratorMiddleware
from utils.utils import Utils
from models.domain_models import Job

# ── App ───────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Video Story Pipeline API",
    description="Generate story videos with TTS audio and burned-in subtitles.",
    version="1.0.0",
)

# ── In-memory job store ───────────────────────────────────────────────────────

jobs: list[Job] = []


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

    job_id = Utils.generate_job_id(jobs)
    jobs.append(
        Job(
            job_id=job_id,
            status="pending",
            output=None,
            error=None,
            duration=None,
        )
    )

    background_tasks.add_task(run_pipeline, job_id, request)

    return JobResponse(
        job_id=job_id,
        status="pending",
        message=f"Job accepted. Poll /status/{job_id} to check progress.",
    )


@app.get("/status/{job_id}", response_model=StatusResponse)
def status(job_id: str):
    """Check the status of a generation job."""

    job = next((j for j in jobs if j.job_id == job_id), None)

    if job == None:
        raise HTTPException(status_code=404, detail="Job not found")

    return StatusResponse(job_id=job_id, **job)


@app.get("/download/{job_id}")
def download(job_id: str):
    """Download the finished video for a completed job."""

    job = next((j for j in jobs if j.job_id == job_id), None)

    if job == None:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status != "done":
        raise HTTPException(
            status_code=400, detail=f"Job is not done yet — status: {job['status']}"
        )

    output_path = Path(job.output)
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
            {"job_id": j.job_id, "status": j.status, "duration": j.duration}
            for j in jobs
        ],
    }
