import json

from src.core import ISessionRepository, Session
from src.repository.base_redis_repository import BaseRedisRepository


class RedisSessionRepository(ISessionRepository, BaseRedisRepository[Session]):

    async def get_session(
        self,
        session_id: str,
    ) -> Session:
        session = await self.get(id=session_id)
        return session

    async def set_session(
        self,
        session: Session,
    ) -> None:
        session_id = session.id
        await self.set(id=session_id, entity=session)
        return

    async def delete_session(
        self,
        session_id: str,
    ) -> None:
        await self.delete(id=session_id)
        return

    def get_prefix(self) -> str:
        return "session-data"

    def to_json(self, entity: Session) -> str:
        return json.dumps(entity.__dict__)

    def from_json(self, json_string: str) -> Session:
        return Session(**json.loads(json_string))
