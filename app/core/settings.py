from pydantic import Field
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)

import app._const as c


class Settings(BaseSettings):
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    REDIS_URL: str = Field(..., env="REDIS_URL")

    BOT_TOKEN: str = Field(..., env="BOT_TOKEN")

    OPENROUTER_API_KEY: str = Field(..., env="OPENROUTER_API_KEY")
    OPENROUTER_API_URL: str = Field(..., env="OPENROUTER_API_URL")

    CONTEXT_MAX_TOKENS: int = Field(..., ge=0, env="CONTEXT_MAX_TOKENS")
    CONTEXT_CUTOFF_THRESHOLD: int = Field(..., ge=0, env="CONTEXT_CUTOFF_THRESHOLD")
    CONTEXT_SUMMARIZE: bool = Field(..., env="CONTEXT_SUMMARIZE")

    SUMMARY_MODEL: str = Field(..., env="SUMMARY_MODEL")
    SUMMARY_MAX_TOKENS: int = Field(..., ge=0, env="SUMMARY_MAX_TOKENS")

    COMPLETION_MODEL: str = Field(..., env="COMPLETION_MODEL")
    COMPLETION_MAX_TOKENS: int = Field(..., ge=0, env="COMPLETION_MAX_TOKENS")
    COMPLETION_TEMPERATURE: int = Field(..., ge=0, le=1, env="COMPLETION_TEMPERATURE")

    MUTE_LOGGERS: list[str] | None = Field(default=c.MUTE_LOGGERS, env="MUTE_LOGGERS")
    DEVELOPERS: list[int] | None = Field(default=c.DEVELOPERS, env="DEVELOPERS")
    DEBUG: bool = Field(default=c.DEBUG, env="DEBUG")

    model_config = SettingsConfigDict(env_file=".env")
