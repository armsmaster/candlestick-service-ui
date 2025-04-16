from src.core import (
    CsrfTokenValidationException,
    ICsrfTokenValidator,
    ISessionRepository,
)


class CsrfTokenValidator(ICsrfTokenValidator):

    def __init__(self, session_repository: ISessionRepository):
        self.session_repository = session_repository

    async def validate(self, csrf_token: str, session_id: str) -> None:
        session = await self.session_repository.get_session(session_id=session_id)
        if csrf_token != session.csrf_token:
            raise CsrfTokenValidationException
        return
