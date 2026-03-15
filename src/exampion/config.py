from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    BOT_TOKEN: str
    ACCOUNTABILITY_PARTNER_ID: int
    REVIEW_TIMEOUT_SECONDS: int


@lru_cache(maxsize=1)
def get_cfg() -> Settings:
    return Settings()  # ty:ignore[missing-argument]
