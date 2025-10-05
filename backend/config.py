from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine.url import URL


class DBSettings(BaseSettings):
    postgres_user: str = Field()
    postgres_password: SecretStr = Field()
    postgres_host: str = Field(default="db")
    pgport: int = Field()
    postgres_db: str = Field()
    postgres_export_port: int = Field(default=5432)

    db_pool_size: int = Field(default=5)
    db_max_overflow: int = Field(default=10)
    db_pool_timeout: int = Field(default=30)

    sqlalchemy_echo: bool = Field(default=False)

    @property
    def db_config(self) -> URL:
        return URL.create(
            "postgresql+asyncpg",
            username=self.postgres_user,
            password=self.postgres_password.get_secret_value(),
            host=self.postgres_host,
            port=self.pgport,
            database=self.postgres_db,
        )


class Settings(DBSettings, BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    debug: bool = Field(default=True)
    expose_docs: bool = Field(default=True)
    version: str = Field(default="")


settings = Settings()
