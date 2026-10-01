import base64
import json
from pathlib import Path

import pytest

from stalehand.run.job import Job, decode, job_id

FIXTURE = json.loads((Path(__file__).parents[2] / "schema" / "fixtures" / "job.json").read_text())


def test_decodes_go_encoded_job():
    job = decode(FIXTURE["base64"])
    assert job == Job(**FIXTURE["job"])
    assert job.guard == "dom_step_abort" and job.seed == 7 and job.max_steps == 12


def test_id_matches_go():
    assert job_id(Job(**FIXTURE["job"])) == FIXTURE["job"]["id"]


def _b64(d):
    return base64.b64encode(json.dumps(d).encode()).decode()


def test_rejects_tampered_id():
    bad = dict(FIXTURE["job"], seed=8)
    with pytest.raises(ValueError, match="id"):
        decode(_b64(bad))


def test_rejects_unknown_field():
    with pytest.raises(ValueError, match="extra"):
        decode(_b64(dict(FIXTURE["job"], extra=1)))


def test_rejects_missing_field():
    d = dict(FIXTURE["job"])
    del d["planner"]
    with pytest.raises(ValueError, match="planner"):
        decode(_b64(d))
