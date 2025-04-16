from abc import ABC, abstractmethod

from redis.asyncio import Redis


class BaseRedisRepository[T](ABC):

    def __init__(self, redis_client: Redis):
        self.redis_client = redis_client

    async def get(self, id: str) -> T | None:
        name = self._construct_key(id=id)
        exists = await self.redis_client.exists(name)
        if exists:
            json_string = await self.redis_client.get(name=name)
            return self.from_json(json_string)
        return None

    async def set(self, id: str, entity: T) -> None:
        name = self._construct_key(id=id)
        await self.redis_client.set(name=name, value=self.to_json(entity))
        return

    async def delete(self, id: str) -> None:
        name = self._construct_key(id=id)
        exists = await self.redis_client.exists(name)
        if exists:
            await self.redis_client.delete(name)
        return None

    def _construct_key(self, id: str) -> str:
        prefix = self.get_prefix()
        return f"{prefix}:{id}"

    @abstractmethod
    def get_prefix(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def to_json(self, entity: T) -> str:
        raise NotImplementedError

    @abstractmethod
    def from_json(self, json_string: str) -> T:
        raise NotImplementedError
