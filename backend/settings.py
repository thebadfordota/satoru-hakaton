from __future__ import annotations

import os

from pydantic import Field, model_validator, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


def get_env_path() -> str:
    return os.environ.get('APP_CONFIG_FILE', '.env')


class Settings(BaseSettings):
    PROJECT_TITLE: str = 'Users'

    SERVER_HOST: str
    SERVER_PORT: int
    SERVER_RELOAD: bool
    SERVER_WORKERS_COUNT: int = 1

    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str
    DB_PORT: int
    DB_HOST: str
    DB_PREFIX: str

    FIREBASE_TOKEN: str

    ECHO_SQL: bool
    DB_URI: str = Field(default='')
    model_config = SettingsConfigDict(
        env_file=get_env_path(),
        case_sensitive=True,
        env_file_encoding='utf-8',
        extra='ignore',
    )

    @model_validator(mode='after')
    def assemble_db_uri(self) -> Settings:
        self.DB_URI = PostgresDsn.build(
            scheme=self.DB_PREFIX,
            username=self.DB_USER,
            password=self.DB_PASSWORD,
            host=self.DB_HOST,
            port=self.DB_PORT,
            path=self.DB_NAME,
        ).unicode_string()
        return self


settings = Settings.model_validate({})
