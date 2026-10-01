"""The job spec the Go runner sends (runner/matrix.Job), decoded and checked against its ID."""
import base64
import hashlib
import json
from dataclasses import dataclass, fields


@dataclass(frozen=True)
class Job:
    id: str
    matrix: str
    scenarios: str
    architecture: str
    guard: str
    planner: str
    executor: str
    seed: int
    max_steps: int
    change_timing: str


def job_id(j: Job) -> str:
    """Same hash as runner/matrix.jobID: every field that changes the result, not the matrix name."""
    key = (f"{j.scenarios}|{j.architecture}|{j.guard}|{j.planner}|{j.executor}|{j.seed}|{j.max_steps}"
           f"|{j.change_timing}")
    return hashlib.sha256(key.encode()).hexdigest()[:12]


def decode(text: str) -> Job:
    raw = json.loads(base64.b64decode(text))
    names = {f.name for f in fields(Job)}
    extra, missing = set(raw) - names, names - set(raw)
    if extra or missing:
        raise ValueError(f"job fields: extra {sorted(extra)}, missing {sorted(missing)}")
    job = Job(**raw)
    if job_id(job) != job.id:
        raise ValueError(f"job id {job.id} does not match its fields ({job_id(job)})")
    return job
