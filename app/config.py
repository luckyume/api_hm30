from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application configuration.

    Values are loaded from environment variables
    and the .env file.
    """

    # ==============================
    # API
    # ==============================

    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # ==============================
    # POWER CONTROLLER
    # ==============================

    power_port: str = "COM5"
    power_baudrate: int = 115200
    power_timeout: float = 2.0

    # ==============================
    # HM30
    # ==============================

    hm30_port: str = "COM8"
    hm30_baudrate: int = 115200
    hm30_heartbeat_timeout: float = 5.0

    # ==============================
    # LOGGING
    # ==============================

    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()