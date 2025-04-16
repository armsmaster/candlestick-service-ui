import json

from src.core import IOauthDataRepository, OauthData
from src.repository.base_redis_repository import BaseRedisRepository


class RedisOauthDataRepository(IOauthDataRepository, BaseRedisRepository[OauthData]):

    async def get_oauth_data(
        self,
        session_id: str,
    ) -> OauthData:
        oauth_data = await self.get(id=session_id)
        return oauth_data

    async def set_oauth_data(
        self,
        session_id: str,
        oauth_data: OauthData,
    ) -> None:
        await self.set(id=session_id, entity=oauth_data)
        return

    async def delete_oauth_data(
        self,
        session_id: str,
    ) -> None:
        await self.delete(id=session_id)
        return

    def get_prefix(self) -> str:
        return "session-oauth-data"

    def to_json(self, entity: OauthData) -> str:
        return json.dumps(entity.__dict__)

    def from_json(self, json_string: str) -> OauthData:
        return OauthData(**json.loads(json_string))
