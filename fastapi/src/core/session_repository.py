from abc import ABC, abstractmethod

from src.core.data_structures import Session


class ISessionRepository(ABC):

    @abstractmethod
    async def get_session(
        self,
        session_id: str,
    ) -> Session | None:
        raise NotImplementedError

    @abstractmethod
    async def set_session(
        self,
        session: Session,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def delete_session(
        self,
        session_id: str,
    ) -> None:
        raise NotImplementedError
