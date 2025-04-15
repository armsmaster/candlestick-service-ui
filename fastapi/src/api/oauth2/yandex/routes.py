import json
from http import HTTPStatus
from typing import Annotated

from fastapi.responses import RedirectResponse
from redis.asyncio import Redis

from fastapi import APIRouter, Cookie, Depends

from src.api.dependency import (
    get_redis_client,
    get_yandex_auth_processor,
    get_yandex_code_processor,
)
from src.config import settings
from src.core import IAuthProcessor, ICodeProcessor

api_router = APIRouter(prefix="/yandex")


@api_router.get(
    "/code",
    response_class=RedirectResponse,
    status_code=HTTPStatus.PERMANENT_REDIRECT,
)
async def yandex_code(
    state: str,
    code: str,
    candles_session: Annotated[str | None, Cookie()] = None,
    redis_client: Redis = Depends(get_redis_client),
    yandex_code_processor: ICodeProcessor = Depends(get_yandex_code_processor),
):
    session_data = await redis_client.get(name=f"session:{candles_session}")
    session_data = json.loads(session_data)
    csrf_token = session_data["csrf_token"]
    if csrf_token != state:
        return {"msg": "csrf_token != state"}

    oauth_data = await yandex_code_processor.get_oauth_data(code=code)
    session_data = {
        "csrf_token": csrf_token,
        "is_authenticated": True,
        "oauth_provider": oauth_data.provider,
        "user_id": oauth_data.user_id,
        "user_email": oauth_data.user_email,
    }

    await redis_client.set(
        name=f"session:{candles_session}",
        value=json.dumps(session_data),
    )
    return RedirectResponse(settings.app.origin_url)


@api_router.get(
    "/auth",
    response_class=RedirectResponse,
    status_code=HTTPStatus.PERMANENT_REDIRECT,
)
async def yandex_auth(
    csrf_token: str,
    candles_session: Annotated[str | None, Cookie()] = None,
    redis_client: Redis = Depends(get_redis_client),
    yandex_auth_processor: IAuthProcessor = Depends(get_yandex_auth_processor),
):
    session_data = await redis_client.get(name=f"session:{candles_session}")
    session_data = json.loads(session_data)
    if csrf_token != session_data["csrf_token"]:
        return {"msg": 'csrf_token != session_data["csrf_token"]'}

    url = await yandex_auth_processor.generate_url(csrf_token=csrf_token)
    return RedirectResponse(url)
