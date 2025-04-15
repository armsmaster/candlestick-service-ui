from typing import AsyncGenerator

import redis

from src.auth_processor import GoogleAuthProcessor, YandexAuthProcessor
from src.config import settings


async def get_redis_client() -> AsyncGenerator[redis.asyncio.Redis, None]:
    redis_client = redis.asyncio.Redis(
        host=settings.redis.host,
        port=settings.redis.port,
        decode_responses=True,
    )
    yield redis_client
    await redis_client.close()


async def get_google_auth_processor() -> AsyncGenerator[GoogleAuthProcessor, None]:
    yield GoogleAuthProcessor()


async def get_yandex_auth_processor() -> AsyncGenerator[YandexAuthProcessor, None]:
    yield YandexAuthProcessor()
