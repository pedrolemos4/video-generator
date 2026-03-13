from pydantic import BaseModel
from typing import Optional


class Job(BaseModel):
    job_id: str
    status: str  # pending | running | done | error
    output: Optional[str] = None
    error: Optional[str] = None
    duration: Optional[float] = None
