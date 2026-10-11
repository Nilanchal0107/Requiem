"""Smoke tests for the V2 catalogue, auth stub, and reports: each endpoint answers and matches the contract models."""
import json

import pytest
from fastapi.testclient import TestClient

from api.contracts import (
    ArchetypeSummary,
    Block,
    District,
    IntakeInput,
    MeOut,
    OkOut,
    Report,
    ReportCreated,
    ReportSummary,
    SchemeSummary,
    StageEvent,
    UserOut,
    Village,
)
from api.main import app

CREDS = {"username": "ramesh", "password": "secret1"}


@pytest.fixture
def client():
    return TestClient(app)


def test_localities_three_shapes_validate_against_contract(client):
    districts = client.get("/api/localities").json()
    assert [District.model_validate(d) for d in districts]

    blocks = client.get("/api/localities", params={"district": "FX-NASHIK"}).json()
    parsed_blocks = [Block.model_validate(b) for b in blocks]
    assert parsed_blocks and all(b.district_code == "FX-NASHIK" for b in parsed_blocks)

    villages = client.get("/api/localities", params={"district": "FX-NASHIK", "block": "FX-NIPHAD"}).json()
    parsed_villages = [Village.model_validate(v) for v in villages]
    assert "Lasalgaon" in {v.name for v in parsed_villages}


def test_localities_unknown_codes(client):
    assert client.get("/api/localities", params={"district": "NOPE"}).json() == []
    assert client.get("/api/localities", params={"district": "FX-NASHIK", "block": "NOPE"}).status_code == 404
    assert client.get("/api/localities", params={"block": "FX-NIPHAD"}).status_code == 404  # block needs its district


def test_archetypes_validate(client):
    body = client.get("/api/archetypes").json()
    assert {ArchetypeSummary.model_validate(a).id for a in body} >= {"dairy"}


def test_schemes_validate(client):
    body = client.get("/api/schemes").json()
    assert {SchemeSummary.model_validate(s).id for s in body} >= {"mudra", "pmegp"}


def test_login_then_me_then_logout(client):
    assert client.get("/api/auth/me").json() == {"user": None}

    login = client.post("/api/auth/login", json=CREDS)
    assert login.status_code == 200
    assert "session" in login.cookies or "session" in client.cookies
    assert UserOut.model_validate(login.json()).username

    me = MeOut.model_validate(client.get("/api/auth/me").json())
    assert me.user is not None

    out = client.post("/api/auth/logout")
    assert OkOut.model_validate(out.json()).ok is True
    assert client.get("/api/auth/me").json() == {"user": None}


def test_register_accepts_valid_body_and_logs_in(client):
    res = client.post("/api/auth/register", json={"username": "priya", "password": "secret1"})
    assert res.status_code == 200
    assert UserOut.model_validate(res.json())
    assert MeOut.model_validate(client.get("/api/auth/me").json()).user is not None


@pytest.mark.parametrize(
    "body",
    [
        {"username": "ab", "password": "secret1"},        # username too short
        {"username": "x" * 31, "password": "secret1"},    # username too long
        {"username": "ramesh", "password": "12345"},      # password too short
    ],
)
@pytest.mark.parametrize("path", ["/api/auth/register", "/api/auth/login"])
def test_malformed_credentials_are_422(client, body, path):
    assert client.post(path, json=body).status_code == 422


def test_tables_are_created_on_startup(tmp_path, monkeypatch):
    from sqlalchemy import create_engine, inspect

    from api.db import create_tables

    engine = create_engine(f"sqlite:///{tmp_path / 'r.db'}")
    create_tables(engine)
    create_tables(engine)  # restart: second run must not fail
    assert {"user", "report", "village"} <= set(inspect(engine).get_table_names())


def test_password_helpers_are_declared_but_not_implemented():
    from api.auth import hash_password, verify_password

    with pytest.raises(NotImplementedError):
        hash_password("secret1")
    with pytest.raises(NotImplementedError):
        verify_password("secret1", "scrypt$00$00")


# --- V1-04: reports and SSE stream ------------------------------------------

STAGES = ["intake", "market", "cost", "schemes", "dpr", "explanation"]
INTAKE = {
    "village_code": "FX1002",
    "archetype_id": "dairy",
    "unit_scale": 5.0,
    "own_contribution": 100000,
    "eligibility": {"age": 34, "gender": "female", "social_category": "obc", "education": "10th_pass"},
    "language": "mr",
}


@pytest.fixture
def no_stage_delay(monkeypatch):
    from api import reports

    monkeypatch.setattr(reports, "STAGE_DELAY_S", 0)


def parse_sse(text):
    events = []
    for block in text.strip().split("\n\n"):
        lines = dict(line.split(": ", 1) for line in block.splitlines())
        events.append((lines["event"], json.loads(lines["data"])))
    return events


def test_post_report_returns_id_and_rejects_bad_body(client):
    res = client.post("/api/reports", json=INTAKE)
    assert res.status_code == 200
    assert ReportCreated.model_validate(res.json()).report_id

    bad = {**INTAKE, "own_contribution": -1}
    assert client.post("/api/reports", json=bad).status_code == 422


def test_stream_replays_six_stages_in_order_then_done(client, no_stage_delay):
    res = client.get("/api/reports/demo-1/stream")
    assert res.status_code == 200
    assert res.headers["content-type"].startswith("text/event-stream")

    events = parse_sse(res.text)
    stage_events = [StageEvent.model_validate(data) for kind, data in events if kind == "stage"]
    assert [e.stage for e in stage_events] == [s for s in STAGES for _ in range(2)]
    assert [e.status for e in stage_events] == ["running", "done"] * 6

    assert events[-1] == ("done", {"report_id": "demo-1"})


def test_get_report_returns_fixture_under_requested_id(client):
    res = client.get("/api/reports/demo-1")
    assert res.status_code == 200
    report = Report.model_validate(res.json())
    assert report.id == "demo-1"
    assert report.engine is not None and report.explanation is not None


def test_list_reports_is_401_for_guest_and_one_summary_after_login(client):
    assert client.get("/api/reports").status_code == 401

    client.post("/api/auth/login", json=CREDS)
    res = client.get("/api/reports")
    assert res.status_code == 200
    summaries = [ReportSummary.model_validate(s) for s in res.json()]
    assert len(summaries) == 1
    assert summaries[0].archetype_id == "dairy"
    assert summaries[0].village_name == "Pimpalgaon Baswant"


def test_run_pipeline_is_declared_but_not_implemented():
    from api.pipeline import run_pipeline

    with pytest.raises(NotImplementedError):
        run_pipeline("demo-1", IntakeInput.model_validate(INTAKE))
