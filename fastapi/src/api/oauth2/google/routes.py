import json
from http import HTTPStatus
from typing import Annotated

import aiohttp
import jwt
import jwt.algorithms
from fastapi.responses import RedirectResponse
from redis.asyncio import Redis

from fastapi import APIRouter, Cookie, Depends

from src.api.dependency import (
    get_google_auth_processor,
    get_google_code_processor,
    get_redis_client,
)
from src.config import settings
from src.core import IAuthProcessor, ICodeProcessor

api_router = APIRouter(prefix="/google")
openid_config_url = "https://accounts.google.com/.well-known/openid-configuration"


async def get_google_jwks_uri_endpoint() -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get(url=openid_config_url) as resp:
            response_json = await resp.json()
            return response_json["jwks_uri"]


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


@api_router.get(
    "/code",
    response_class=RedirectResponse,
    status_code=HTTPStatus.PERMANENT_REDIRECT,
)
async def google_code(
    state: str,
    code: str,
    scope: str,
    candles_session: Annotated[str | None, Cookie()] = None,
    redis_client: Redis = Depends(get_redis_client),
    google_code_processor: ICodeProcessor = Depends(get_google_code_processor),
) -> RedirectResponse:
    session_data = await redis_client.get(name=f"session:{candles_session}")
    session_data = json.loads(session_data)
    csrf_token = session_data["csrf_token"]
    if csrf_token != state:
        return {"msg": "csrf_token != state"}

    oauth_data = await google_code_processor.get_oauth_data(code=code)
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
async def google_auth(
    csrf_token: str,
    candles_session: Annotated[str | None, Cookie()] = None,
    redis_client: Redis = Depends(get_redis_client),
    google_auth_processor: IAuthProcessor = Depends(get_google_auth_processor),
):
    session_data = await redis_client.get(name=f"session:{candles_session}")
    session_data = json.loads(session_data)
    if csrf_token != session_data["csrf_token"]:
        return {"msg": 'csrf_token != session_data["csrf_token"]'}
    url = await google_auth_processor.generate_url(csrf_token=csrf_token)
    return RedirectResponse(url)
