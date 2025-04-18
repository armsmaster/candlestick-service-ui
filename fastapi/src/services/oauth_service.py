from abc import ABC, abstractmethod
from typing import Literal

from src.core import (
    IAuthProcessor,
    ICodeProcessor,
    IOauthDataRepository,
    ISessionRepository,
)


class IOauthService(ABC):

    OAUTH_PROVIDER = Literal["google", "yandex"]

    @abstractmethod
    def __init__(
        self,
        session_repository: ISessionRepository,
        oauth_data_repository: IOauthDataRepository,
    ):
        raise NotImplementedError

    @abstractmethod
    async def get_auth_url(
        self,
        oauth_provider: OAUTH_PROVIDER,
        csrf_token: str,
    ) -> str:
        raise NotImplementedError

    @abstractmethod
    async def process_auth_response(
        self,
        oauth_provider: OAUTH_PROVIDER,
        code: str,
        session_id: str,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def auth_processor_factory(self, oauth_provider: OAUTH_PROVIDER) -> IAuthProcessor:
        raise NotImplementedError

    @abstractmethod
    def code_processor_factory(self, oauth_provider: OAUTH_PROVIDER) -> ICodeProcessor:
        raise NotImplementedError
