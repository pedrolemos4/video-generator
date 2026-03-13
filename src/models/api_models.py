#!/usr/bin/env python3
"""
models.py
---------
Request and response models for the Video Story Pipeline API.

All requests share a base `type` field. The middleware uses this
to decide which pipeline to run and which fields to expect.
"""

from typing import Literal, Optional
from pydantic import BaseModel
from utils.global_variables import Variables


# ── Base ──────────────────────────────────────────────────────────────────────


class BaseVideoRequest(BaseModel):
    type: str


# ── Request types ─────────────────────────────────────────────────────────────


class StoryRequest(BaseVideoRequest):
    type: Literal["story"] = "story"
    title: str
    story: str
    voice: str = Variables.DEFAULT_VOICE
    model: str = Variables.WHISPER_MODEL
    source: str = Variables.SOURCE_VIDEO


class ClipsRequest(BaseVideoRequest):
    type: Literal["clips"] = "clips"
    content: bytes


# ── Response types ────────────────────────────────────────────────────────────


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
