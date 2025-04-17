from src.auth_processor import GoogleAuthProcessor, YandexAuthProcessor
from src.code_processor import GoogleCodeProcessor, YandexCodeProcessor
from src.core import (
    IAuthProcessor,
    ICodeProcessor,
    IOauthDataRepository,
    ISessionRepository,
)
from src.services.oauth_service import IOauthService


class OauthService(IOauthService):

    def __init__(
        self,
        session_repository: ISessionRepository,
        oauth_data_repository: IOauthDataRepository,
    ):
        self.session_repository = session_repository
        self.oauth_data_repository = oauth_data_repository

    async def get_auth_url(
        self,
        oauth_provider: IOauthService.OAUTH_PROVIDER,
        csrf_token: str,
    ) -> str:
        auth_processor = self.auth_processor_factory(oauth_provider)
        url = await auth_processor.generate_url(csrf_token=csrf_token)
        return url

    async def process_auth_response(
        self,
        oauth_provider: IOauthService.OAUTH_PROVIDER,
        code: str,
        session_id: str,
    ) -> None:
        code_processor = self.code_processor_factory(oauth_provider)

        oauth_data = await code_processor.get_oauth_data(code=code)
        await self.oauth_data_repository.set_oauth_data(
            session_id=session_id,
            oauth_data=oauth_data,
        )

        session = await self.session_repository.get_session(session_id=session_id)
        session.oauth_provider = oauth_data.provider
        session.user_id = oauth_data.user_id
        session.user_email = oauth_data.user_email
        await self.session_repository.set_session(session=session)

        return

    def auth_processor_factory(
        self,
        oauth_provider: IOauthService.OAUTH_PROVIDER,
    ) -> IAuthProcessor:
        if oauth_provider == "google":
            return GoogleAuthProcessor()
        if oauth_provider == "yandex":
            return YandexAuthProcessor()
        raise ValueError(f"{oauth_provider=}")

    def code_processor_factory(
        self,
        oauth_provider: IOauthService.OAUTH_PROVIDER,
    ) -> ICodeProcessor:
        if oauth_provider == "google":
            return GoogleCodeProcessor()
        if oauth_provider == "yandex":
            return YandexCodeProcessor()
        raise ValueError(f"{oauth_provider=}")
