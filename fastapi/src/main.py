from fastapi.middleware.cors import CORSMiddleware

from fastapi import FastAPI

from src.api import api_router
from src.config import settings

app = FastAPI(
    root_path="/ui-backend",
    title=settings.app.title,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.app.origin_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router)
