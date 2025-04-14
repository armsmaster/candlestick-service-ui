__all__ = [
    "router_oauth",
]

from fastapi import APIRouter

from src.api.oauth2.google import api_router as api_router_oauth_google
from src.api.oauth2.yandex import api_router as api_router_oauth_yandex

router_oauth = APIRouter(prefix="/oauth2", tags=["oauth"])
router_oauth.include_router(api_router_oauth_google)
router_oauth.include_router(api_router_oauth_yandex)
