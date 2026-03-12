from typing import Optional
from pydantic import BaseModel
from utils.global_variables import Variables

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
