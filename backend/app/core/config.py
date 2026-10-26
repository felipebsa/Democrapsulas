from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="../.env", extra="ignore")

    SECRET_KEY: str
    ALGORITHM: str
    TOKEN_EXPIRED: int
    DATABASE_URL: str

    #capsule limits
    CAPSULES_PER_DAY: int = 5
    CAPSULE_COOLDOWN_SECONDS: int = 120
    HALL_CAPSULE_LIMIT: int = 30

settings = Settings()
