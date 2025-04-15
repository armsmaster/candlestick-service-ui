from abc import ABC, abstractmethod

from src.core.data_structures import OauthData


class ICodeProcessor(ABC):
    """Class responsible for retrieving user tokens from external Oauth API."""

    @abstractmethod
    def get_token(self, csrf_token: str, code: str, scope: str) -> OauthData:
        raise NotImplementedError
