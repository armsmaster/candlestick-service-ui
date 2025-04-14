import json
import urllib.parse
from http import HTTPStatus
from typing import Annotated
from uuid import uuid4

import aiohttp
from fastapi.responses import RedirectResponse
from redis.asyncio import Redis

from fastapi import APIRouter, Cookie, Depends

from src.api.dependency import get_redis_client
from src.config import settings

api_router = APIRouter(prefix="/yandex")


async def get_yandex_authorization_endpoint() -> str:
    return "https://oauth.yandex.ru/authorize"


async def get_yandex_token_endpoint() -> str:
    return "https://oauth.yandex.ru/token"


async def get_yandex_user_info_endpoint() -> str:
    return "https://login.yandex.ru/info"


async def get_yandex_token(code: str) -> dict:
    token_endpoint = await get_yandex_token_endpoint()
    payload = {
        "code": code,
        "client_id": settings.oauth.yandex.client_id,
        "client_secret": settings.oauth.yandex.client_secret,
        "grant_type": "authorization_code",
    }
    payload = aiohttp.FormData(payload)
    headers = {
        "Content-type": "application/x-www-form-urlencoded",
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(
            url=token_endpoint,
            data=payload,
            headers=headers,
        ) as resp:
            response_data = await resp.json()
            return response_data


async def get_yandex_user_info(access_token: str) -> dict:
    yandex_user_info_endpoint = await get_yandex_user_info_endpoint()
    headers = {
        "Authorization": f"bearer {access_token}",
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url=yandex_user_info_endpoint, headers=headers) as resp:
            user_info = await resp.json()
            return user_info


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
):
    session_data = await redis_client.get(name=f"session:{candles_session}")
    session_data = json.loads(session_data)
    csrf_token = session_data["csrf_token"]
    if csrf_token != state:
        return {"msg": "csrf_token != state"}
    session_data["yandex"] = {
        "code": code,
        "token": await get_yandex_token(code=code),
    }
    session_data["yandex"]["user_info"] = await get_yandex_user_info(
        session_data["yandex"]["token"]["access_token"]
    )
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
):
    session_data = await redis_client.get(name=f"session:{candles_session}")
    session_data = json.loads(session_data)
    if csrf_token != session_data["csrf_token"]:
        return {"msg": 'csrf_token != session_data["csrf_token"]'}
    authorization_endpoint = await get_yandex_authorization_endpoint()
    params = {
        "client_id": settings.oauth.yandex.client_id,
        "response_type": "code",
        "scope": "login:email",
        "redirect_uri": settings.oauth.yandex.redirect_uri,
        "state": csrf_token,
        "nonce": uuid4().hex,
        "force_confirm": "yes",
    }
    url = authorization_endpoint + "?"
    url += urllib.parse.urlencode(params)
    return RedirectResponse(url)
