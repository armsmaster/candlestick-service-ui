from abc import ABC, abstractmethod

from src.core.data_structures import Session


class ISessionMaker(ABC):

    @abstractmethod
    async def create_session(self) -> Session:
        raise NotImplementedError
