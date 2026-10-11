import os

from dotenv import load_dotenv
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from api import auth, catalog, chat, compare, intake, reports, simulate, voice

load_dotenv()

app = FastAPI(title="Requiem")
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SESSION_SECRET", "change-me"), same_site="lax")

for module in (auth, catalog, intake, reports, simulate, compare, chat, voice):
    app.include_router(module.router)
