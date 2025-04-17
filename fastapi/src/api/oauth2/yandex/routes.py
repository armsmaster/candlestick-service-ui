from http import HTTPStatus
from typing import Annotated, Awaitable, Callable

from fastapi.responses import RedirectResponse

from fastapi import APIRouter, Cookie, Depends

from src.api.dependency import (
    csrf_token_validate,
    get_oauth_data_repository,
    get_session_repository,
    get_yandex_auth_processor,
    get_yandex_code_processor,
)
from src.config import settings
from src.core import (
    IAuthProcessor,
    ICodeProcessor,
    IOauthDataRepository,
    ISessionRepository,
)

api_router = APIRouter(prefix="/yandex")


@api_router.get(
    "/code",
    response_class=RedirectResponse,
    status_code=HTTPStatus.PERMANENT_REDIRECT,
)
async def yandex_code(
    state: str,
    code: str,
    sessionid: Annotated[str | None, Cookie()] = None,
    yandex_code_processor: ICodeProcessor = Depends(get_yandex_code_processor),
    session_repository: ISessionRepository = Depends(get_session_repository),
    oauth_data_repository: IOauthDataRepository = Depends(get_oauth_data_repository),
    csrf_validate: Callable[[str, str], Awaitable] = Depends(csrf_token_validate),
):
    await csrf_validate(state, sessionid)

    oauth_data = await yandex_code_processor.get_oauth_data(code=code)
    await oauth_data_repository.set_oauth_data(
        session_id=sessionid,
        oauth_data=oauth_data,
    )

    session = await session_repository.get_session(session_id=sessionid)
    session.oauth_provider = oauth_data.provider
    session.user_id = oauth_data.user_id
    session.user_email = oauth_data.user_email

    await session_repository.set_session(session=session)

    return RedirectResponse(settings.app.origin_url)


@api_router.get(
    "/auth",
    response_class=RedirectResponse,
    status_code=HTTPStatus.PERMANENT_REDIRECT,
)
async def yandex_auth(
    csrf_token: str,
    sessionid: Annotated[str | None, Cookie()] = None,
    yandex_auth_processor: IAuthProcessor = Depends(get_yandex_auth_processor),
    session_repository: ISessionRepository = Depends(get_session_repository),
    csrf_validate: Callable[[str, str], Awaitable] = Depends(csrf_token_validate),
):
    await csrf_validate(csrf_token, sessionid)

    url = await yandex_auth_processor.generate_url(csrf_token=csrf_token)
    return RedirectResponse(url)
