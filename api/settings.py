"""Env-driven settings and the fixture loader. Kept apart from main.py so routers can import it without a cycle. V3 removes USE_FIXTURES."""
import json
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from fastapi import HTTPException

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./requiem.db")
SESSION_SECRET = os.getenv("SESSION_SECRET", "change-me")
USE_FIXTURES = os.getenv("USE_FIXTURES", "1").lower() not in ("0", "false", "no", "off")

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures"


def fixture(name: str) -> Any:
    """Load a JSON file from fixtures/. Routes that need it return 501 when USE_FIXTURES is off."""
    if not USE_FIXTURES:
        raise HTTPException(501, "fixtures disabled")
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))
