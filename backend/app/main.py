from fastapi import FastAPI

from app.api.router import router as api_router
from app.core.config import app_name, version


app = FastAPI(title=app_name, version=version)
app.include_router(api_router)
