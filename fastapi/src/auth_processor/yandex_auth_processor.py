import urllib.parse
from uuid import uuid4

from src.config import settings
from src.core import IAuthProcessor


class YandexAuthProcessor(IAuthProcessor):

    AUTH_ENDPOINT = "https://oauth.yandex.ru/authorize"

    async def generate_url(self, csrf_token):
        params = {
            "client_id": settings.oauth.yandex.client_id,
            "response_type": "code",
            "scope": settings.oauth.yandex.scope,
            "redirect_uri": settings.oauth.yandex.redirect_uri,
            "state": csrf_token,
            "nonce": uuid4().hex,
            "force_confirm": "yes",
        }
        url = self.AUTH_ENDPOINT + "?"
        url += urllib.parse.urlencode(params)
        return url
