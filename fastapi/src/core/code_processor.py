from abc import ABC, abstractmethod

from src.core.data_structures import OauthData


class ICodeProcessor(ABC):
    """Class responsible for retrieving user tokens from external Oauth API."""

    @abstractmethod
    async def get_oauth_data(self, code: str) -> OauthData:
        raise NotImplementedError
