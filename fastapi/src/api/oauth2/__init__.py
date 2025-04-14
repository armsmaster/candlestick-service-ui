__all__ = [
    "router_oauth",
]
from src.api.oauth2.google import api_router as api_router_oauth_google
from fastapi import APIRouter

router_oauth = APIRouter(prefix="/oauth2", tags=["oauth"])
router_oauth.include_router(api_router_oauth_google)
