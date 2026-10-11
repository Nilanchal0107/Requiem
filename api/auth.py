import hashlib
import secrets

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from api.contracts import Credentials, MeOut, OkOut, UserOut
from api.db import User
from api.deps import current_user, get_session

router = APIRouter(prefix="/api/auth", tags=["auth"])

SCRYPT = {"n": 2**14, "r": 8, "p": 1}


def hash_password(password: str) -> str:
    """scrypt$<salt hex>$<hash hex>."""
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode(), salt=salt, **SCRYPT)
    return f"scrypt${salt.hex()}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        scheme, salt_hex, hash_hex = stored.split("$")
        salt, expected = bytes.fromhex(salt_hex), bytes.fromhex(hash_hex)
    except ValueError:
        return False
    if scheme != "scrypt":
        return False
    return secrets.compare_digest(hashlib.scrypt(password.encode(), salt=salt, **SCRYPT), expected)


def _sign_in(request: Request, user: User) -> UserOut:
    out = UserOut(id=user.id, username=user.username)
    request.session["user"] = out.model_dump()
    return out


@router.post("/register", response_model=UserOut)
def register(body: Credentials, request: Request, session: Session = Depends(get_session)):
    user = User(username=body.username, password_hash=hash_password(body.password))
    session.add(user)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(409, "username already taken")
    session.refresh(user)
    return _sign_in(request, user)


@router.post("/login", response_model=UserOut)
def login(body: Credentials, request: Request, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.username == body.username)).first()
    if user is None or not verify_password(body.password, user.password_hash):
        raise HTTPException(401, "wrong username or password")
    return _sign_in(request, user)


@router.post("/logout", response_model=OkOut)
def logout(request: Request):
    request.session.clear()
    return OkOut()


@router.get("/me", response_model=MeOut)
def me(user: UserOut | None = Depends(current_user)):
    return MeOut(user=user)
