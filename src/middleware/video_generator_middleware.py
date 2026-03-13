#!/usr/bin/env python3
"""
middleware/video_generator.py
-----------------------------
Middleware that receives a generation request, decides which pipeline
to run based on the video type, and updates the job store accordingly.

Supported types:
    "story"  — TTS + subtitles + background video
    "clips"  — split video into clips + subtitles per clip
"""

import traceback
from typing import Union

from fastapi import HTTPException
import time
from pathlib import Path

from features.story_background import StoryBackground
from models.api_models import ClipsRequest, StoryRequest
from models.domain_models import Job
from utils.utils import Utils


class VideoGeneratorMiddleware:

    def __init__(self, jobs: list[Job]):
        self.jobs = jobs

    async def run(
        self, job_id: str, request: Union[StoryRequest, ClipsRequest]
    ) -> None:
        """
        Decide which pipeline to run based on request.type
        and update the job store with the result.
        """

        job = next((j for j in self.jobs if j.job_id == job_id), None)

        if job == None:
            raise HTTPException(status_code=404, detail="Job not found")

        job.status = "running"
        start = time.time()

        try:
            output_file = await self._dispatch(request, job_id)

            job.status = "done"
            job.output = str(output_file.resolve())
            job.duration = round(time.time() - start, 2)

        except Exception as e:
            job.status = "error"
            job.error = str(e)
            Utils.log(f"Job {job_id} failed: {e}", "❌")
            Utils.log(traceback.format_exc(), "🔴")

    # Implement new pipeline
    async def _dispatch(
        self, request: Union[StoryRequest, ClipsRequest], job_id: str
    ) -> Path:
        """Route to the correct pipeline based on request.type."""

        if request.type == "story":
            pipeline = StoryBackground(
                voice=request.voice,
                model=request.model,
                source_video=request.source,
            )
            return await pipeline.run(request.title, request.story, job_id=job_id)

        elif request.type == "clips":
            raise NotImplementedError("clips pipeline not yet implemented")

        else:
            raise ValueError(f"Unknown video type: '{request.type}'")
