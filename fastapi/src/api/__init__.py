__all__ = [
    "api_router",
]

from src.api.session import api_router as api_router_session
from fastapi import APIRouter

api_router = APIRouter()
api_router.include_router(api_router_session)
