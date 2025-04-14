import json
from typing import Annotated
from uuid import uuid4

import jwt
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

    if "google" in session_data:
        id_token = session_data["google"]["token"]["id_token"]
        id_token_claims = jwt.decode(id_token, options={"verify_signature": False})
        user_id = id_token_claims["sub"]
        user_email = id_token_claims["email"]
        return SessionData(
            csrf_token=csrf_token,
            is_authenticated=True,
            oauth_provider="google",
            user_id=user_id,
            user_email=user_email,
            debug_info=session_data,
        )

    if "yandex" in session_data:
        user_info = session_data["yandex"]["user_info"]
        user_id = user_info["id"]
        user_email = user_info["default_email"]
        return SessionData(
            csrf_token=csrf_token,
            is_authenticated=True,
            oauth_provider="yandex",
            user_id=user_id,
            user_email=user_email,
            debug_info=session_data,
        )

    return SessionData(
        csrf_token=csrf_token,
        is_authenticated=False,
        oauth_provider=None,
        user_id=None,
        user_email=None,
        debug_info=session_data,
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
