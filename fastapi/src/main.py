import urllib.parse
from fastapi import FastAPI, Cookie
from fastapi.responses import Response, RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import jwt.algorithms
from pydantic import BaseModel
from uuid import uuid4
from typing import Annotated
from os import environ
import redis
import json
import aiohttp
import urllib
import jwt
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


class CsrfToken(BaseModel):
    token: str


async def get_redis_client() -> redis.asyncio.Redis:
    redis_client = redis.asyncio.Redis(
        host=settings.redis.host,
        port=settings.redis.port,
        decode_responses=True,
    )
    return redis_client


async def get_google_authorization_endpoint() -> str:
    openid_config_url = "https://accounts.google.com/.well-known/openid-configuration"
    async with aiohttp.ClientSession() as session:
        async with session.get(url=openid_config_url) as resp:
            response_json = await resp.json()
            return response_json["authorization_endpoint"]


async def get_google_token_endpoint() -> str:
    openid_config_url = "https://accounts.google.com/.well-known/openid-configuration"
    async with aiohttp.ClientSession() as session:
        async with session.get(url=openid_config_url) as resp:
            response_json = await resp.json()
            return response_json["token_endpoint"]


async def get_google_jwks_uri_endpoint() -> str:
    openid_config_url = "https://accounts.google.com/.well-known/openid-configuration"
    async with aiohttp.ClientSession() as session:
        async with session.get(url=openid_config_url) as resp:
            response_json = await resp.json()
            return response_json["jwks_uri"]


async def get_yandex_authorization_endpoint() -> str:
    return "https://oauth.yandex.ru/authorize"


async def get_yandex_token_endpoint() -> str:
    return "https://oauth.yandex.ru/token"


async def get_yandex_user_info_endpoint() -> str:
    return "https://login.yandex.ru/info"


async def get_google_token(code: str) -> dict:
    token_endpoint = await get_google_token_endpoint()
    payload = {
        "code": code,
        "client_id": settings.oauth.google.client_id,
        "client_secret": settings.oauth.google.client_secret,
        "redirect_uri": settings.oauth.google.redirect_uri,
        "grant_type": "authorization_code",
    }
    payload = aiohttp.FormData(payload)
    async with aiohttp.ClientSession() as session:
        async with session.post(url=token_endpoint, data=payload) as resp:
            response_data = await resp.json()
            return response_data


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


async def validate_google_id_token(id_token: str) -> bool:
    print(f"{id_token=}")
    jwks_uri = await get_google_jwks_uri_endpoint()
    async with aiohttp.ClientSession() as session:
        async with session.get(url=jwks_uri) as resp:
            jwks = await resp.json()

    public_keys = {}
    for jwk in jwks["keys"]:
        kid = jwk["kid"]
        public_keys[kid] = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(jwk))

    kid = jwt.get_unverified_header(id_token)["kid"]
    print(f"{kid=}")
    key = public_keys[kid]
    print(f"{key=}")

    try:
        payload = jwt.decode(
            id_token,
            key=key,
            algorithms=["RS256"],
            options={
                "verify_aud": False,
                "verify_signature": True,
            },
        )
        print("validate_google_id_token:ok")
        return True
    except Exception as e:
        print("validate_google_id_token:exc")
        print(f"{e=}")
        return False


@app.get("/oauth2/google/code")
async def google_code(
    state: str,
    code: str,
    scope: str,
    candles_session: Annotated[str | None, Cookie()] = None,
):
    redis_client = await get_redis_client()
    session_data = await redis_client.get(name=f"session:{candles_session}")
    session_data = json.loads(session_data)
    csrf_token = session_data["csrf_token"]
    if csrf_token != state:
        await redis_client.close()
        return {"msg": "csrf_token != state"}
    session_data["google"] = {
        "code": code,
        "scope": scope,
        "token": await get_google_token(code=code),
    }
    await redis_client.set(
        name=f"session:{candles_session}",
        value=json.dumps(session_data),
    )
    await redis_client.close()
    return RedirectResponse(settings.app.origin_url)


@app.get("/oauth2/google/auth")
async def google_auth(
    csrf_token: str,
    candles_session: Annotated[str | None, Cookie()] = None,
):
    redis_client = await get_redis_client()
    session_data = await redis_client.get(name=f"session:{candles_session}")
    session_data = json.loads(session_data)
    if csrf_token != session_data["csrf_token"]:
        await redis_client.close()
        return {"msg": 'csrf_token != session_data["csrf_token"]'}
    authorization_endpoint = await get_google_authorization_endpoint()
    params = {
        "client_id": settings.oauth.google.client_id,
        "response_type": "code",
        "scope": "openid email",
        "redirect_uri": settings.oauth.google.redirect_uri,
        "state": csrf_token,
        "nonce": uuid4().hex,
        "access_type": "offline",
        "prompt": "consent",
    }
    url = authorization_endpoint + "?"
    url += urllib.parse.urlencode(params)
    await redis_client.close()
    return RedirectResponse(url)


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


@app.get("/csrf-token")
async def get_csrf_token(
    candles_session: Annotated[str | None, Cookie()] = None,
) -> CsrfToken:
    redis_client = await get_redis_client()
    session_data = await redis_client.get(name=f"session:{candles_session}")
    session_data = json.loads(session_data)
    if "csrf_token" in session_data:
        return CsrfToken(token=session_data["csrf_token"])
    session_data["csrf_token"] = f"csrf:{uuid4().hex}"
    await redis_client.set(
        name=f"session:{candles_session}",
        value=json.dumps(session_data),
    )
    await redis_client.close()
    return CsrfToken(token=session_data["csrf_token"])


@app.get("/session")
async def session(candles_session: Annotated[str | None, Cookie()] = None):
    redis_client = await get_redis_client()
    if candles_session is None:
        session = uuid4().hex
        await redis_client.set(name=f"session:{session}", value="{}")
        session_data = dict()
    else:
        session = candles_session
        session_data = await redis_client.get(name=f"session:{session}")
        session_data = json.loads(session_data)
    if "google" in session_data and "token" not in session_data["google"]:
        token = await get_google_token(code=session_data["google"]["code"])
        session_data["google"]["token"] = token
        await redis_client.set(
            name=f"session:{candles_session}",
            value=json.dumps(session_data),
        )
    if "google" in session_data and "token" in session_data["google"]:
        id_token = session_data["google"]["token"]["id_token"]
        id_token_claims = jwt.decode(id_token, options={"verify_signature": False})
        id_token_headers = jwt.get_unverified_header(id_token)
        session_data["google"]["token"]["id_token_claims"] = id_token_claims
        session_data["google"]["token"]["id_token_headers"] = id_token_headers
        session_data["google"]["token"]["id_token_is_valid"] = (
            await validate_google_id_token(id_token)
        )
    if "yandex" in session_data and "token" in session_data["yandex"]:
        if "user_info" not in session_data["yandex"]:
            session_data["yandex"]["user_info"] = await get_yandex_user_info(
                session_data["yandex"]["token"]["access_token"]
            )
            await redis_client.set(
                name=f"session:{candles_session}",
                value=json.dumps(session_data),
            )
    response = JSONResponse(session_data)
    response.set_cookie(key="candles_session", value=session)
    await redis_client.close()
    return response


@app.delete("/session")
async def session(candles_session: Annotated[str | None, Cookie()] = None):
    redis_client = await get_redis_client()
    if candles_session is not None:
        session = candles_session
        await redis_client.delete(f"session:{session}")
    session = uuid4().hex
    await redis_client.set(name=f"session:{session}", value="{}")
    await redis_client.close()
    response = Response()
    response.set_cookie(key="candles_session", value=session)
    return response
