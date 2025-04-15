import json
from typing import Annotated
from uuid import uuid4

from redis.asyncio import Redis

from fastapi import APIRouter, Cookie, Depends, Response

from src.api.dependency import get_redis_client
from src.api.session.schemas import SessionData

api_router = APIRouter(prefix="/session", tags=["session"])


@api_router.get("/")
async def get_session(
    response: Response,
    candles_session: Annotated[str | None, Cookie()] = None,
    redis_client: Redis = Depends(get_redis_client),
) -> SessionData:
    if candles_session is None:
        session = uuid4().hex
        session_data = {"csrf_token": f"csrf:{uuid4().hex}"}
        response.set_cookie(key="candles_session", value=session)
        await redis_client.set(
            name=f"session:{session}",
            value=json.dumps(session_data),
        )
    else:
        session = candles_session
        session_data = await redis_client.get(name=f"session:{session}")
        session_data = json.loads(session_data)

    csrf_token = session_data["csrf_token"]

    if "is_authenticated" in session_data:
        return SessionData(
            csrf_token=session_data["csrf_token"],
            is_authenticated=session_data["is_authenticated"],
            oauth_provider=session_data["oauth_provider"],
            user_id=session_data["user_id"],
            user_email=session_data["user_email"],
            debug_info={},
        )

    return SessionData(
        csrf_token=csrf_token,
        is_authenticated=False,
        oauth_provider=None,
        user_id=None,
        user_email=None,
        debug_info={},
    )


@api_router.delete("/")
async def reset_session(
    response: Response,
    candles_session: Annotated[str | None, Cookie()] = None,
    redis_client: Redis = Depends(get_redis_client),
) -> SessionData:
    if candles_session is not None:
        session = candles_session
        await redis_client.delete(f"session:{session}")

    session = uuid4().hex
    session_data = {"csrf_token": f"csrf:{uuid4().hex}"}
    await redis_client.set(
        name=f"session:{session}",
        value=json.dumps(session_data),
    )
    response.set_cookie(key="candles_session", value=session)

    return SessionData(
        csrf_token=session_data["csrf_token"],
        is_authenticated=False,
        oauth_provider=None,
        user_id=None,
        user_email=None,
        debug_info=session_data,
    )
