import aiohttp
import jwt

from src.config import settings
from src.core import ICodeProcessor, OauthData


class GoogleCodeProcessor(ICodeProcessor):

    PROVIDER = "google"
    OPENID_CONFIG_URL = "https://accounts.google.com/.well-known/openid-configuration"

    async def get_oauth_data(self, code: str) -> OauthData:
        openid_config = await self._get_openid_config()
        token_endpoint = self._get_token_endpoint(openid_config=openid_config)
        token_data = await self._get_token(endpoint=token_endpoint, code=code)

        access_token = token_data["access_token"]
        refresh_token = token_data["refresh_token"]
        id_token = token_data["id_token"]
        token_type = token_data["token_type"]

        id_token_claims = await self._get_token_claims(token=id_token)
        user_id = id_token_claims["sub"]
        user_email = id_token_claims["email"]

        oauth_data = OauthData(
            provider=self.PROVIDER,
            access_token=access_token,
            refresh_token=refresh_token,
            token_type=token_type,
            id_token=id_token,
            user_id=user_id,
            user_email=user_email,
        )
        return oauth_data

    async def _get_openid_config(self) -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.get(url=self.OPENID_CONFIG_URL) as resp:
                openid_config = await resp.json()
                return openid_config

    def _get_token_endpoint(self, openid_config: dict) -> str:
        return openid_config["token_endpoint"]

    async def _get_token(self, endpoint: str, code: str):
        payload = {
            "code": code,
            "client_id": settings.oauth.google.client_id,
            "client_secret": settings.oauth.google.client_secret,
            "redirect_uri": settings.oauth.google.redirect_uri,
            "grant_type": "authorization_code",
        }
        payload = aiohttp.FormData(payload)
        async with aiohttp.ClientSession() as session:
            async with session.post(url=endpoint, data=payload) as resp:
                token_data = await resp.json()
                return token_data

    async def _get_token_claims(self, token: str) -> dict:
        return jwt.decode(token, options={"verify_signature": False})
