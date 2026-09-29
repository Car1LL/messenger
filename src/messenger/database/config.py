from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_NAME: str
    DATABASE_PORT: int
    DATABASE_HOST: str
    DATABASE_PASS: str
    DATABASE_USER: str

    TEST_DATABASE_NAME: str

    @property
    def DATABASE_URL(self):
        return (
            f"postgresql+asyncpg://{self.DATABASE_USER}:{self.DATABASE_PASS}"
            f"@{self.DATABASE_HOST}:{self.DATABASE_PORT}"
            f"/{self.DATABASE_NAME}"
        )

    @property
    def TEST_DATABASE_URL(self):
        return (
            f"postgresql+asyncpg://{self.DATABASE_USER}:{self.DATABASE_PASS}"
            f"@{self.DATABASE_HOST}:{self.DATABASE_PORT}"
            f"/{self.TEST_DATABASE_NAME}"
        )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
