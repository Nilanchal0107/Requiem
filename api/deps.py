from collections.abc import Iterator

from fastapi import Depends, HTTPException, Request
from sqlmodel import Session

from api import db
from api.contracts import UserOut


def get_session() -> Iterator[Session]:
    with Session(db.engine) as session:
        yield session


def current_user(request: Request) -> UserOut | None:
    user = request.session.get("user")
    return UserOut(**user) if user else None


def require_user(user: UserOut | None = Depends(current_user)) -> UserOut:
    if user is None:
        raise HTTPException(401, "login required")
    return user
