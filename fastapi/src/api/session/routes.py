from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, Response

from src.api.dependency import (
    get_cookie_policy,
    get_session_service,
)
from src.api.session.schemas import SessionSchema
from src.services import ISessionService

api_router = APIRouter(prefix="/session", tags=["session"])


@api_router.get("/")
async def get_session(
    response: Response,
    sessionid: Annotated[str | None, Cookie()] = None,
    session_service: ISessionService = Depends(get_session_service),
    cookie_policy: dict = Depends(get_cookie_policy),
) -> SessionSchema:
    session = await session_service.get_session(session_id=sessionid)
    response.set_cookie(key="sessionid", value=session.id, **cookie_policy)
    return SessionSchema.from_session(session)


@api_router.delete("/")
async def reset_session(
    response: Response,
    sessionid: Annotated[str | None, Cookie()] = None,
    session_service: ISessionService = Depends(get_session_service),
    cookie_policy: dict = Depends(get_cookie_policy),
) -> SessionSchema:
    session = await session_service.drop_session(session_id=sessionid)
    response.set_cookie(key="sessionid", value=session.id, **cookie_policy)
    return SessionSchema.from_session(session)
