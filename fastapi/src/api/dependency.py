from typing import AsyncGenerator

from redis.asyncio import Redis

from fastapi import Depends

from src.auth_processor import GoogleAuthProcessor, YandexAuthProcessor
from src.code_processor import GoogleCodeProcessor, YandexCodeProcessor
from src.config import settings
from src.repository import RedisSessionRepository
from src.session_maker import SessionMaker


async def get_redis_client() -> AsyncGenerator[Redis, None]:
    redis_client = Redis(
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


async def get_google_code_processor() -> AsyncGenerator[GoogleCodeProcessor, None]:
    yield GoogleCodeProcessor()


async def get_yandex_code_processor() -> AsyncGenerator[YandexCodeProcessor, None]:
    yield YandexCodeProcessor()


async def get_session_repository(
    redis_client: Redis = Depends(get_redis_client),
) -> AsyncGenerator[RedisSessionRepository, None]:
    yield RedisSessionRepository(redis_client=redis_client)


async def get_session_maker() -> AsyncGenerator[SessionMaker, None]:
    yield SessionMaker()
