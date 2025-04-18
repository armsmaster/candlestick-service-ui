from abc import ABC, abstractmethod

from src.core import ISessionRepository


class ICsrfTokenValidator(ABC):

    @abstractmethod
    def __init__(self, session_repository: ISessionRepository):
        raise NotImplementedError

    @abstractmethod
    async def validate(self, csrf_token: str, session_id: str) -> None:
        raise NotImplementedError
