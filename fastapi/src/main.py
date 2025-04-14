import json
import urllib
import urllib.parse
from typing import Annotated
from uuid import uuid4

import aiohttp
import redis
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from fastapi import Cookie, FastAPI

from src.api import api_router
from src.config import settings

app = FastAPI(
    root_path="/ui-backend",
    title=settings.app.title,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.app.origin_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router)


async def get_redis_client() -> redis.asyncio.Redis:
    redis_client = redis.asyncio.Redis(
        host=settings.redis.host,
        port=settings.redis.port,
        decode_responses=True,
    )
    return redis_client


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


@app.get("/oauth2/yandex/code")
async def yandex_code(
    state: str,
    code: str,
    candles_session: Annotated[str | None, Cookie()] = None,
):
    redis_client = await get_redis_client()
    session_data = await redis_client.get(name=f"session:{candles_session}")
    session_data = json.loads(session_data)
    csrf_token = session_data["csrf_token"]
    if csrf_token != state:
        await redis_client.close()
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
    await redis_client.close()
    return RedirectResponse(settings.app.origin_url)


@app.get("/oauth2/yandex/auth")
async def yandex_auth(
    csrf_token: str,
    candles_session: Annotated[str | None, Cookie()] = None,
):
    redis_client = await get_redis_client()
    session_data = await redis_client.get(name=f"session:{candles_session}")
    session_data = json.loads(session_data)
    if csrf_token != session_data["csrf_token"]:
        await redis_client.close()
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
    await redis_client.close()
    return RedirectResponse(url)
