from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import router as api_router
from app.core.config import app_name, should_create_tables_on_startup, version
from app.db.init_db import create_db_tables


@asynccontextmanager
async def lifespan(_: FastAPI):
    if should_create_tables_on_startup:
        create_db_tables()
    yield


app = FastAPI(title=app_name, version=version, lifespan=lifespan)
app.include_router(api_router)
