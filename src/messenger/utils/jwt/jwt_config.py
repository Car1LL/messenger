from pydantic_settings import SettingsConfigDict, BaseSettings

class JWTSettings(BaseSettings):
    SECRET_KEY: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

jwt_settings = JWTSettings()