"""Smoke tests for the V2 catalogue, auth stub, and reports: each endpoint answers and matches the contract models."""
import json

import pytest
from fastapi.testclient import TestClient

from api.contracts import (
    ArchetypeSummary,
    Block,
    ChatResponse,
    Comparison,
    District,
    EngineResult,
    IntakeInput,
    IntakeParseResponse,
    MeOut,
    OkOut,
    Report,
    ReportCreated,
    ReportSummary,
    SchemeSummary,
    StageEvent,
    TranscribeResponse,
    UserOut,
    Village,
)
from api.main import app

CREDS = {"username": "ramesh", "password": "secret1"}


@pytest.fixture
def db_engine(tmp_path):
    from sqlmodel import create_engine

    from api.db import create_tables

    engine = create_engine(f"sqlite:///{tmp_path / 'test.db'}")
    create_tables(engine)
    return engine


@pytest.fixture
def client(db_engine):
    """A fresh SQLite database per test, swapped in through the session dependency."""
    from sqlmodel import Session

    from api.deps import get_session

    def session_override():
        with Session(db_engine) as session:
            yield session

    app.dependency_overrides[get_session] = session_override
    yield TestClient(app)
    app.dependency_overrides.clear()


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

    client.post("/api/auth/register", json=CREDS)
    client.post("/api/auth/logout")
    login = client.post("/api/auth/login", json=CREDS)
    assert login.status_code == 200
    assert "session" in login.cookies or "session" in client.cookies
    assert UserOut.model_validate(login.json()).username

    me = MeOut.model_validate(client.get("/api/auth/me").json())
    assert me.user is not None and me.user.username == CREDS["username"]

    out =client.post("/api/auth/logout")
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


def test_register_twice_is_409(client):
    assert client.post("/api/auth/register", json=CREDS).status_code == 200
    assert client.post("/api/auth/register", json=CREDS).status_code == 409


def test_wrong_password_and_unknown_user_get_same_401(client):
    client.post("/api/auth/register", json=CREDS)
    client.post("/api/auth/logout")

    wrong = client.post("/api/auth/login", json={**CREDS, "password": "wrong-one"})
    unknown = client.post("/api/auth/login", json={"username": "nobody", "password": "secret1"})
    assert wrong.status_code == unknown.status_code == 401
    assert wrong.json() == unknown.json()
    assert client.get("/api/auth/me").json() == {"user": None}


def test_stored_password_is_scrypt_not_plain_text(client, db_engine):
    from sqlmodel import Session, select

    from api.auth import verify_password
    from api.db import User

    client.post("/api/auth/register", json=CREDS)
    with Session(db_engine) as session:
        stored = session.exec(select(User)).one().password_hash
    assert stored != CREDS["password"] and stored.startswith("scrypt$")
    assert verify_password(CREDS["password"], stored)
    assert not verify_password("wrong-one", stored)
    assert not verify_password(CREDS["password"], "not-a-hash")


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

    client.post("/api/auth/register", json=CREDS)
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


# --- V1-05: simulate, compare, chat, intake parse, voice transcribe ---------

FIXTURE_REPORT_ID = "demo-niphad-dairy"


def test_simulate_returns_fixture_engine_result(client):
    res = client.post("/api/simulate", json=INTAKE)
    assert res.status_code == 200
    engine = EngineResult.model_validate(res.json())
    assert engine.verdict.level in {"feasible", "feasible_with_changes", "not_feasible"}
    assert "funding_gap" in engine.figures


def test_simulate_rejects_bad_body(client):
    assert client.post("/api/simulate", json={**INTAKE, "own_contribution": -1}).status_code == 422


def test_compare_returns_one_result_per_archetype_in_request_order(client):
    body = {"input": INTAKE, "archetype_ids": ["poultry", "dairy"]}
    res = client.post("/api/compare", json=body)
    assert res.status_code == 200
    comparison = Comparison.model_validate(res.json())
    assert [r.archetype_id for r in comparison.results] == ["poultry", "dairy"]
    assert comparison.language == "mr"
    assert "{{poultry.min_dscr}}" in comparison.summary and "{{dairy.min_dscr}}" in comparison.summary


def test_compare_unknown_archetype_is_400(client):
    body = {"input": INTAKE, "archetype_ids": ["dairy", "nope"]}
    assert client.post("/api/compare", json=body).status_code == 400


@pytest.mark.parametrize("ids", [["dairy"], ["dairy", "poultry", "kirana", "tailoring"]])
def test_compare_one_or_four_archetypes_is_422(client, ids):
    assert client.post("/api/compare", json={"input": INTAKE, "archetype_ids": ids}).status_code == 422


def test_chat_returns_contract_response_with_citation_and_change(client):
    body = {"report_id": FIXTURE_REPORT_ID, "message": "Can I borrow less?", "language": "en"}
    res = client.post("/api/chat", json=body)
    assert res.status_code == 200
    chat = ChatResponse.model_validate(res.json())
    assert len(chat.citations) == 1 and len(chat.suggested_changes) == 1
    assert chat.tools_used


def test_chat_unknown_report_is_404(client):
    body = {"report_id": "no-such-report", "message": "hi", "language": "en"}
    assert client.post("/api/chat", json=body).status_code == 404


def test_intake_parse_returns_partial_fields_and_missing(client):
    res = client.post("/api/intake/parse", json={"text": "I want a dairy with five cows", "language": "en"})
    assert res.status_code == 200
    parsed = IntakeParseResponse.model_validate(res.json())
    assert parsed.fields["archetype_id"] == "dairy"
    assert "village_code" in parsed.missing


def test_voice_transcribe_returns_text(client):
    files = {"audio": ("note.webm", b"\x1a\x45\xdf\xa3", "audio/webm")}
    res = client.post("/api/voice/transcribe", files=files, data={"language": "en"})
    assert res.status_code == 200
    assert TranscribeResponse.model_validate(res.json()).text
