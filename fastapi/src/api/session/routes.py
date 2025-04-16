from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, Response

from src.api.dependency import (
    get_cookie_policy,
    get_oauth_data_repository,
    get_session_maker,
    get_session_repository,
)
from src.api.session.schemas import SessionSchema
from src.core import IOauthDataRepository, ISessionMaker, ISessionRepository

api_router = APIRouter(prefix="/session", tags=["session"])


@api_router.get("/")
async def get_session(
    response: Response,
    sessionid: Annotated[str | None, Cookie()] = None,
    session_repository: ISessionRepository = Depends(get_session_repository),
    session_maker: ISessionMaker = Depends(get_session_maker),
    cookie_policy: dict = Depends(get_cookie_policy),
) -> SessionSchema:
    if sessionid is None:
        session = session_maker.create_session()
        await session_repository.set_session(session=session)
    else:
        session = await session_repository.get_session(session_id=sessionid)
    response.set_cookie(key="sessionid", value=session.id, **cookie_policy)
    return SessionSchema.from_session(session)


@api_router.delete("/")
async def reset_session(
    response: Response,
    sessionid: Annotated[str | None, Cookie()] = None,
    session_repository: ISessionRepository = Depends(get_session_repository),
    oauth_data_repository: IOauthDataRepository = Depends(get_oauth_data_repository),
    session_maker: ISessionMaker = Depends(get_session_maker),
    cookie_policy: dict = Depends(get_cookie_policy),
) -> SessionSchema:
    if sessionid is not None:
        await session_repository.delete_session(session_id=sessionid)
        await oauth_data_repository.delete_oauth_data(session_id=sessionid)

    session = session_maker.create_session()
    await session_repository.set_session(session=session)
    response.set_cookie(key="sessionid", value=session.id, **cookie_policy)

    return SessionSchema.from_session(session)
