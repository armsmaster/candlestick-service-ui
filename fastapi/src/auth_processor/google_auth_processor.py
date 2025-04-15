import urllib.parse
from uuid import uuid4

import aiohttp

from src.config import settings
from src.core import IAuthProcessor


class GoogleAuthProcessor(IAuthProcessor):

    OPENID_CONFIG_URL = "https://accounts.google.com/.well-known/openid-configuration"

    async def generate_url(self, csrf_token):
        openid_config = await self._get_openid_config()
        authorization_endpoint = self._get_authorization_endpoint(openid_config)
        params = {
            "client_id": settings.oauth.google.client_id,
            "response_type": "code",
            "scope": settings.oauth.google.scope,
            "redirect_uri": settings.oauth.google.redirect_uri,
            "state": csrf_token,
            "nonce": uuid4().hex,
            "access_type": "offline",
            "prompt": "consent",
        }
        url = authorization_endpoint + "?"
        url += urllib.parse.urlencode(params)
        return url

    async def _get_openid_config(self) -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.get(url=self.OPENID_CONFIG_URL) as resp:
                openid_config = await resp.json()
                return openid_config

    def _get_authorization_endpoint(self, openid_config: dict) -> str:
        return openid_config["authorization_endpoint"]
