from fastapi import APIRouter, HTTPException

from api.contracts import Credentials, MeOut, OkOut, UserOut

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=UserOut)
def register(body: Credentials):
    raise HTTPException(501)


@router.post("/login", response_model=UserOut)
def login(body: Credentials):
    raise HTTPException(501)


@router.post("/logout", response_model=OkOut)
def logout():
    raise HTTPException(501)


@router.get("/me", response_model=MeOut)
def me():
    raise HTTPException(501)
