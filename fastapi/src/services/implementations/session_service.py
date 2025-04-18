from src.core import IOauthDataRepository, ISessionMaker, ISessionRepository, Session
from src.services import ISessionService


class SessionService(ISessionService):

    def __init__(
        self,
        session_repository: ISessionRepository,
        oauth_data_repository: IOauthDataRepository,
        session_maker: ISessionMaker,
    ):
        self.session_repository = session_repository
        self.oauth_data_repository = oauth_data_repository
        self.session_maker = session_maker

    async def get_session(self, session_id: str | None) -> Session:
        session = self._fetch_session(session_id=session_id)
        if session is None:
            session = self.session_maker.create_session()
            await self.session_repository.set_session(session=session)
        return session

    async def drop_session(self, session_id: str) -> Session:
        if session_id is not None:
            await self.session_repository.delete_session(session_id=session_id)
            await self.oauth_data_repository.delete_oauth_data(session_id=session_id)

        session = self.session_maker.create_session()
        await self.session_repository.set_session(session=session)
        return session

    async def _fetch_session(self, session_id: str | None) -> Session | None:
        if session_id is None:
            return None

        session = await self.session_repository.get_session(session_id=session_id)
        return session
