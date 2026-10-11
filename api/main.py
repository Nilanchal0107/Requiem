from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from api import auth, catalog, chat, compare, intake, reports, simulate, voice
from sqlmodel import Session

from api.db import create_tables, engine
from api.demo_seed import seed_demo
from api.settings import SESSION_SECRET
from data.loaders import seed_villages


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    with Session(engine) as session:
        seed_villages(session)
        seed_demo(session)
    yield


app = FastAPI(title="Requiem", lifespan=lifespan)
app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET, same_site="lax")

for module in (auth, catalog, intake, reports, simulate, compare, chat, voice):
    app.include_router(module.router)
