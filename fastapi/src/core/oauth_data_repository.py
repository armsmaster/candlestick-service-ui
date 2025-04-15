from abc import ABC, abstractmethod

from src.core.data_structures import OauthData


class IOauthDataRepository(ABC):

    @abstractmethod
    async def get_oauth_data(
        self,
        session_id: str,
    ) -> OauthData:
        raise NotImplementedError

    @abstractmethod
    async def set_oauth_data(
        self,
        session_id: str,
        session: OauthData,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def delete_oauth_data(
        self,
        session_id: str,
    ) -> None:
        raise NotImplementedError
