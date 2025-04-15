import aiohttp

from src.config import settings
from src.core import ICodeProcessor, OauthData


class YandexCodeProcessor(ICodeProcessor):

    PROVIDER = "yandex"
    TOKEN_ENDPOINT = "https://oauth.yandex.ru/token"
    USER_INFO_ENDPOINT = "https://login.yandex.ru/info"

    async def get_oauth_data(self, code: str) -> OauthData:
        token_data = await self._get_token(code=code)

        access_token = token_data["access_token"]
        refresh_token = token_data["refresh_token"]
        token_type = token_data["token_type"]

        user_info = await self._get_user_info(access_token=access_token)

        user_id = user_info["id"]
        user_email = user_info["default_email"]

        oauth_data = OauthData(
            provider=self.PROVIDER,
            access_token=access_token,
            refresh_token=refresh_token,
            token_type=token_type,
            id_token=None,
            user_id=user_id,
            user_email=user_email,
        )
        return oauth_data

    async def _get_token(self, code: str) -> dict:
        payload = aiohttp.FormData(
            {
                "code": code,
                "client_id": settings.oauth.yandex.client_id,
                "client_secret": settings.oauth.yandex.client_secret,
                "grant_type": "authorization_code",
            }
        )
        headers = {
            "Content-type": "application/x-www-form-urlencoded",
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url=self.TOKEN_ENDPOINT,
                data=payload,
                headers=headers,
            ) as resp:
                token_response = await resp.json()
                return token_response

    async def _get_user_info(self, access_token: str) -> dict:
        headers = {
            "Authorization": f"bearer {access_token}",
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url=self.USER_INFO_ENDPOINT,
                headers=headers,
            ) as resp:
                user_info = await resp.json()
                return user_info
