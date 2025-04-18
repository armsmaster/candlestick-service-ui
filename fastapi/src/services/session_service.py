from abc import ABC, abstractmethod

from src.core import IOauthDataRepository, ISessionMaker, ISessionRepository, Session


class ISessionService(ABC):

    @abstractmethod
    def __init__(
        self,
        session_repository: ISessionRepository,
        oauth_data_repository: IOauthDataRepository,
        session_maker: ISessionMaker,
    ):
        raise NotImplementedError

    @abstractmethod
    async def get_session(session_id: str | None) -> Session:
        raise NotImplementedError

    @abstractmethod
    async def drop_session(session_id: str) -> Session:
        raise NotImplementedError
