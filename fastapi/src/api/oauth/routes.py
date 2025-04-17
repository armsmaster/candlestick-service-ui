from enum import Enum
from http import HTTPStatus
from typing import Annotated, Awaitable, Callable

from fastapi.responses import RedirectResponse

from fastapi import APIRouter, Cookie, Depends

from src.api.dependency import (
    csrf_token_validate,
    get_oauth_service,
)
from src.config import settings
from src.services import IOauthService

api_router = APIRouter(prefix="/oauth", tags=["oauth"])


class OauthProvider(Enum):
    google = "google"
    yandex = "yandex"


@api_router.get(
    "/{oauth_provider}/code",
    response_class=RedirectResponse,
    status_code=HTTPStatus.PERMANENT_REDIRECT,
)
async def process_response(
    oauth_provider: OauthProvider,
    state: str,
    code: str,
    scope: str = None,
    sessionid: Annotated[str | None, Cookie()] = None,
    oauth_service: IOauthService = Depends(get_oauth_service),
    csrf_validate: Callable[[str, str], Awaitable] = Depends(csrf_token_validate),
) -> RedirectResponse:
    await csrf_validate(state, sessionid)
    await oauth_service.process_auth_response(
        oauth_provider=oauth_provider.value,
        code=code,
        session_id=sessionid,
    )
    return RedirectResponse(settings.app.origin_url)


@api_router.get(
    "/{oauth_provider}/auth",
    response_class=RedirectResponse,
    status_code=HTTPStatus.PERMANENT_REDIRECT,
)
async def auth(
    oauth_provider: OauthProvider,
    csrf_token: str,
    sessionid: Annotated[str | None, Cookie()] = None,
    oauth_service: IOauthService = Depends(get_oauth_service),
    csrf_validate: Callable[[str, str], Awaitable] = Depends(csrf_token_validate),
) -> RedirectResponse:
    await csrf_validate(csrf_token, sessionid)
    url = await oauth_service.get_auth_url(
        oauth_provider=oauth_provider.value,
        csrf_token=csrf_token,
    )
    return RedirectResponse(url)
