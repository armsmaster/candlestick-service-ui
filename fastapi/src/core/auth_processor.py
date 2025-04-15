from abc import ABC, abstractmethod


class IAuthProcessor(ABC):
    """Class responsible for generating external Oauth URI."""

    @abstractmethod
    async def generate_url(self, csrf_token: str) -> str:
        raise NotImplementedError
