from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    database_url: str = "sqlite:///./dat_san_local.db"
    jwt_secret: str = "CHANGE-ME-IN-PRODUCTION-DEV-ONLY"
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 240
    seed_demo_data: bool = False
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    def validate_production(self) -> None:
        if self.app_env == "production" and (
            self.jwt_secret == "CHANGE-ME-IN-PRODUCTION-DEV-ONLY"
            or len(self.jwt_secret) < 32
            or self.seed_demo_data
        ):
            raise RuntimeError("Production requires strong JWT_SECRET and SEED_DEMO_DATA=false")


settings = Settings()
settings.validate_production()
