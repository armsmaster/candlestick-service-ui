from dataclasses import dataclass


@dataclass
class OauthData:
    provider: str

    access_token: str
    refresh_token: str
    token_type: str
    id_token: str | None

    user_id: str
    user_email: str
