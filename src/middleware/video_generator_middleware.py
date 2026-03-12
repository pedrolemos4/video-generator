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

import time
from pathlib import Path

from features.story_background import StoryBackground


class VideoGeneratorMiddleware:

    def __init__(self, jobs: dict):
        self.jobs = jobs

    async def run(self, job_id: str, request) -> None:
        """
        Decide which pipeline to run based on request.type
        and update the job store with the result.
        """
        self.jobs[job_id]["status"] = "running"
        start = time.time()

        try:
            output_file = await self._dispatch(request, job_id)

            self.jobs[job_id]["status"] = "done"
            self.jobs[job_id]["output"] = str(output_file.resolve())
            self.jobs[job_id]["duration"] = round(time.time() - start, 2)

        except Exception as e:
            self.jobs[job_id]["status"] = "error"
            self.jobs[job_id]["error"] = str(e)

    async def _dispatch(self, request, job_id: str) -> Path:
        """Route to the correct pipeline based on request.type."""

        if request.type == "story":
            pipeline = StoryBackground(
                voice=request.voice,
                model=request.model,
                source_video=request.source,
            )
            return await pipeline.run(request.story, job_id=job_id)

        elif request.type == "clips":
            raise NotImplementedError("clips pipeline not yet implemented")

        else:
            raise ValueError(f"Unknown video type: '{request.type}'")
