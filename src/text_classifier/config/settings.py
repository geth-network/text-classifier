from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from text_classifier.common_types import FrozenModel


class RabbitSettings(FrozenModel):
    url: SecretStr


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        extra="forbid",
        frozen=True,
        env_ignore_empty=True,
        env_nested_delimiter="__",
        env_parse_none_str="null",
        env_prefix="TEXT_CLASSIFIER__",
    )
    rabbit: RabbitSettings


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
