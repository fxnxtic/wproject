from pathlib import Path
from typing import Any

import yaml
from pydantic import Field
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)

import app._const as c


class YamlConfigSettingsSource(PydanticBaseSettingsSource):
    def __init__(
        self, settings_cls: type[BaseSettings], yaml_file: Path | str = "settings.yaml"
    ) -> None:
        super().__init__(settings_cls)
        self.yaml_file = Path(yaml_file)

    def get_field_value(self, field, field_name: str) -> tuple[Any, str, bool]:
        if not self.yaml_file.exists():
            return None, field_name, False

        with open(self.yaml_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        if field_name in data:
            return data[field_name], field_name, True

        return None, field_name, False

    def prepare_field_value(self, field, value: Any) -> Any:
        return value

    def __call__(self) -> dict[str, Any]:
        if not self.yaml_file.exists():
            return {}

        with open(self.yaml_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        # Only keep fields relevant to this settings class
        return {k: v for k, v in data.items() if k in self.settings_cls.model_fields}


class Settings(BaseSettings):
    db_url: str = Field(..., env="DB_URL")
    redis_url: str = Field(..., env="REDIS_URL")

    bot_token: str = Field(..., env="BOT_TOKEN")
    bot_api_url: str = Field(env="BOT_API_URL", default=c.BOT_API_URL)

    mute_loggers: list[str] | None = c.MUTE_LOGGERS
    developers: list[int] | None = c.DEVELOPERS
    debug: bool = c.DEBUG

    model_config = SettingsConfigDict(env_file=".env")

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls,
        init_settings,
        env_settings,
        dotenv_settings,
        file_secret_settings,
    ):
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            file_secret_settings,
        )
