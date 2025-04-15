from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    title: str
    origin_url: str

    model_config = SettingsConfigDict(env_prefix="APP_")


class RedisSettings(BaseSettings):
    host: str
    port: int

    model_config = SettingsConfigDict(env_prefix="REDIS_")


class OauthGoogleSettings(BaseSettings):
    client_id: str
    client_secret: str
    redirect_uri: str
    scope: str

    model_config = SettingsConfigDict(env_prefix="OAUTH2_GOOGLE_")


class OauthYandexSettings(BaseSettings):
    client_id: str
    client_secret: str
    redirect_uri: str
    scope: str

    model_config = SettingsConfigDict(env_prefix="OAUTH2_YANDEX_")


class OauthSettings(BaseSettings):

    google: OauthGoogleSettings = Field(default_factory=OauthGoogleSettings)
    yandex: OauthYandexSettings = Field(default_factory=OauthYandexSettings)


class Settings(BaseSettings):

    oauth: OauthSettings = Field(default_factory=OauthSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    app: AppSettings = Field(default_factory=AppSettings)
