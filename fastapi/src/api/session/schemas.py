from typing import Self

from pydantic import BaseModel

from src.core import Session


class SessionSchema(BaseModel):
    csrf_token: str
    is_authenticated: bool
    oauth_provider: str | None
    user_id: str | None
    user_email: str | None
    debug_info: dict | None

    @classmethod
    def from_session(session: Session) -> Self:
        if session.oauth_provider != "":
            is_authenticated = True
            oauth_provider = session.oauth_provider
            user_id = session.user_id
            user_email = session.user_email
        else:
            is_authenticated = False
            oauth_provider = None
            user_id = None
            user_email = None

        return SessionSchema(
            csrf_token=session.csrf_token,
            is_authenticated=is_authenticated,
            oauth_provider=oauth_provider,
            user_id=user_id,
            user_email=user_email,
            debug_info={},
        )
