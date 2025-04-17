__all__ = [
    "api_router",
]

from fastapi import APIRouter

from src.api.oauth import router_oauth
from src.api.session import api_router as api_router_session

api_router = APIRouter()
api_router.include_router(api_router_session)
api_router.include_router(router_oauth)
