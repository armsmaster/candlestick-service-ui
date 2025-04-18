from http import HTTPStatus
from typing import AsyncGenerator, Awaitable, Callable

from redis.asyncio import Redis

from fastapi import Depends, HTTPException

from src.config import settings
from src.core import (
    CsrfTokenValidationException,
    IOauthDataRepository,
    ISessionMaker,
    ISessionRepository,
)
from src.csrf_token_validator import CsrfTokenValidator
from src.repository import RedisOauthDataRepository, RedisSessionRepository
from src.services import IOauthService, ISessionService, OauthService, SessionService
from src.session_maker import SessionMaker


async def get_redis_client() -> AsyncGenerator[Redis, None]:
    redis_client = Redis(
        host=settings.redis.host,
        port=settings.redis.port,
        decode_responses=True,
    )
    yield redis_client
    await redis_client.close()


async def get_session_repository(
    redis_client: Redis = Depends(get_redis_client),
) -> AsyncGenerator[RedisSessionRepository, None]:
    yield RedisSessionRepository(redis_client=redis_client)


async def get_oauth_data_repository(
    redis_client: Redis = Depends(get_redis_client),
) -> AsyncGenerator[RedisOauthDataRepository, None]:
    yield RedisOauthDataRepository(redis_client=redis_client)


async def get_session_maker() -> AsyncGenerator[SessionMaker, None]:
    yield SessionMaker()


async def get_oauth_service(
    session_repository: ISessionRepository = Depends(get_session_repository),
    oauth_data_repository: IOauthDataRepository = Depends(get_oauth_data_repository),
) -> AsyncGenerator[IOauthService, None]:

    yield OauthService(
        session_repository=session_repository,
        oauth_data_repository=oauth_data_repository,
    )


async def get_session_service(
    session_repository: ISessionRepository = Depends(get_session_repository),
    oauth_data_repository: IOauthDataRepository = Depends(get_oauth_data_repository),
    session_maker: ISessionMaker = Depends(get_session_maker),
) -> AsyncGenerator[ISessionService, None]:

    yield SessionService(
        session_repository=session_repository,
        oauth_data_repository=oauth_data_repository,
        session_maker=session_maker,
    )


async def csrf_token_validate(
    session_repository: ISessionRepository = Depends(get_session_repository),
) -> AsyncGenerator[Callable[[str, str], Awaitable[None]], None]:

    async def inner(csrf_token: str, session_id: str):
        csrf_token_validator = CsrfTokenValidator(session_repository=session_repository)
        try:
            await csrf_token_validator.validate(
                csrf_token=csrf_token,
                session_id=session_id,
            )
        except CsrfTokenValidationException:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail="CSRF Validation Error",
            )

    yield inner


async def get_cookie_policy() -> AsyncGenerator[dict, None]:
    yield {
        "secure": True,
        "httponly": True,
        "expires": settings.app.cookie_expiry_days * settings.app.seconds_in_day,
    }
