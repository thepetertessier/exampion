from functools import lru_cache

from pydantic import SecretStr  # noqa: TC002
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    BOT_TOKEN: SecretStr
    ACCOUNTABILITY_PARTNER_ID: int = 697929430760292423
    MY_ID: int = 648179895880384534
    REVIEW_TIMEOUT_SECONDS: int = 3600  # 1 hour


@lru_cache(maxsize=1)
def get_cfg() -> Settings:
    return Settings()  # ty:ignore[missing-argument]
