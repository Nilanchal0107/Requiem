from fastapi import APIRouter, Depends, Request

from api.contracts import Credentials, MeOut, OkOut, UserOut
from api.deps import current_user

router = APIRouter(prefix="/api/auth", tags=["auth"])

# shortcut: stub login, any valid body signs in this fixture user, no DB lookup. Real scrypt + user table lookup + 409/401 arrive in V2.
STUB_USER = {"id": 1, "username": "demo"}


def hash_password(password: str) -> str:
    """scrypt$<salt hex>$<hash hex>. Declared for V2; not implemented yet."""
    raise NotImplementedError


def verify_password(password: str, stored: str) -> bool:
    raise NotImplementedError


@router.post("/register", response_model=UserOut)
def register(body: Credentials, request: Request):
    request.session["user"] = STUB_USER
    return STUB_USER


@router.post("/login", response_model=UserOut)
def login(body: Credentials, request: Request):
    request.session["user"] = STUB_USER
    return STUB_USER


@router.post("/logout", response_model=OkOut)
def logout(request: Request):
    request.session.clear()
    return OkOut()


@router.get("/me", response_model=MeOut)
def me(user: UserOut | None = Depends(current_user)):
    return MeOut(user=user)
