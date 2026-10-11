from fastapi import Depends, HTTPException, Request

from api.contracts import UserOut


def current_user(request: Request) -> UserOut | None:
    user = request.session.get("user")
    return UserOut(**user) if user else None


def require_user(user: UserOut | None = Depends(current_user)) -> UserOut:
    if user is None:
        raise HTTPException(401, "login required")
    return user
