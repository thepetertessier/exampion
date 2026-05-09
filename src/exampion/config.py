from datetime import datetime, time, timedelta  # noqa: TC003
from functools import lru_cache
from zoneinfo import ZoneInfo

from loguru import logger
from pydantic import SecretStr  # noqa: TC002
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    BOT_TOKEN: SecretStr
    ACCOUNTABILITY_PARTNER_ID: int = 697929430760292423
    MY_ID: int = 648179895880384534
    REVIEW_TIMEOUT_SECONDS: int = 3600  # 1 hour
    REVIEW_START_TIME: time = time(22)
    REVIEW_TIMEZONE: ZoneInfo = ZoneInfo("America/New_York")

    @property
    def review_delay(self) -> timedelta:
        tz = self.REVIEW_TIMEZONE
        now = datetime.now(tz)
        start_dt = datetime.combine(now.date(), self.REVIEW_START_TIME, tzinfo=tz)
        return start_dt - now


@lru_cache(maxsize=1)
def get_cfg() -> Settings:
    cfg = Settings()  # ty:ignore[missing-argument]
    cfg_str = "\n".join(f"{key}={value!r}" for key, value in cfg.model_dump().items())
    logger.debug(f"Settings: \n{cfg_str}")
    return cfg
