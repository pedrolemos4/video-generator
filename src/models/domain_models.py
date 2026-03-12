from typing import TypedDict, Optional


class Job(TypedDict):
    job_id: str
    status: str  # pending | running | done | error
    output: Optional[str]
    error: Optional[str]
    duration: Optional[float]
