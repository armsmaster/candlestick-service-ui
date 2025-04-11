from pydantic import BaseModel


class SessionData(BaseModel):
    csrf_token: str
    is_authenticated: bool
    oauth_provider: str | None
    user_id: str | None
    user_email: str | None
    debug_info: dict | None
