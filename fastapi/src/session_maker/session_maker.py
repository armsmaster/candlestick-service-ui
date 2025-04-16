from secrets import token_urlsafe

from src.core import ISessionMaker, Session


class SessionMaker(ISessionMaker):

    def create_session(self) -> Session:
        session_id = token_urlsafe(64)
        csrf_token = token_urlsafe(128)
        session = Session(
            id=session_id,
            csrf_token=csrf_token,
            oauth_provider="",
            user_id="",
            user_email="",
        )
        return session
