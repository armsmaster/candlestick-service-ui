from abc import ABC, abstractmethod


class ICsrfTokenValidator(ABC):

    @abstractmethod
    async def validate(self, csrf_token: str, session_id: str) -> None:
        raise NotImplementedError
