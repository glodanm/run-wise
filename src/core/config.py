from pydantic_settings import BaseSettings, SettingsConfigDict


class Configurations(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str
    DB_ECHO: bool
    SECRET_KEY: str
    REFRESH_SECRET_KEY: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
