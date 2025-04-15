from dataclasses import dataclass


@dataclass
class Session:
    id: str
    csrf_token: str

    oauth_provider: str
    user_id: str
    user_email: str
