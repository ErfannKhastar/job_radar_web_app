"""
Core configuration module for the application.

This module uses pydantic-settings to load, validate, and manage
environment variables and application settings.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables or a .env file.

    Pydantic automatically validates the data types. For example, it ensures
    that `database_port` is successfully parsed as an integer.
    """

    # --- Database Configurations ---
    database_host: str
    database_port: int
    database_user: str
    database_password: str
    database_name: str

    # --- Security and Authentication ---
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    refresh_token_expire_days: int

    # --- Third-Party Integrations ---
    # Optional token for Telegram notifications
    telegram_bot_token: str | None = None

    # --- API Configurations ---
    # Prefix for API routing
    api_v1_str: str = "/api/v1"

    # --- Pydantic Model Configuration ---
    # Loads variables from the .env file and ignores extra variables
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


# Instantiate a global settings object to be imported and used across the app
settings = Settings()
