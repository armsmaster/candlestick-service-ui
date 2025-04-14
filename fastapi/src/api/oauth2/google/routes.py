import json
import urllib.parse
from typing import Annotated
from uuid import uuid4

import aiohttp
import jwt
import jwt.algorithms
from fastapi.responses import RedirectResponse
from redis.asyncio import Redis

from fastapi import APIRouter, Cookie, Depends

from src.api.dependency import get_redis_client
from src.config import settings

api_router = APIRouter(prefix="/google")
openid_config_url = "https://accounts.google.com/.well-known/openid-configuration"


async def get_google_authorization_endpoint() -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get(url=openid_config_url) as resp:
            response_json = await resp.json()
            return response_json["authorization_endpoint"]


async def get_google_token_endpoint() -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get(url=openid_config_url) as resp:
            response_json = await resp.json()
            return response_json["token_endpoint"]


async def get_google_jwks_uri_endpoint() -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get(url=openid_config_url) as resp:
            response_json = await resp.json()
            return response_json["jwks_uri"]


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


async def validate_google_id_token(id_token: str) -> bool:
    jwks_uri = await get_google_jwks_uri_endpoint()
    async with aiohttp.ClientSession() as session:
        async with session.get(url=jwks_uri) as resp:
            jwks = await resp.json()

    public_keys = {}
    for jwk in jwks["keys"]:
        kid = jwk["kid"]
        public_keys[kid] = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(jwk))

    kid = jwt.get_unverified_header(id_token)["kid"]
    key = public_keys[kid]

    try:
        jwt.decode(
            id_token,
            key=key,
            algorithms=["RS256"],
            options={
                "verify_aud": False,
                "verify_signature": True,
            },
        )
        return True
    except Exception as e:
        print(f"validate_google_id_token:exc {e=}")
        return False


@api_router.get("/code")
async def google_code(
    state: str,
    code: str,
    scope: str,
    candles_session: Annotated[str | None, Cookie()] = None,
    redis_client: Redis = Depends(get_redis_client),
) -> RedirectResponse:
    session_data = await redis_client.get(name=f"session:{candles_session}")
    session_data = json.loads(session_data)
    csrf_token = session_data["csrf_token"]
    if csrf_token != state:
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
    return RedirectResponse(settings.app.origin_url)


@api_router.get("/auth")
async def google_auth(
    csrf_token: str,
    candles_session: Annotated[str | None, Cookie()] = None,
    redis_client: Redis = Depends(get_redis_client),
):
    session_data = await redis_client.get(name=f"session:{candles_session}")
    session_data = json.loads(session_data)
    if csrf_token != session_data["csrf_token"]:
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
    return RedirectResponse(url)
