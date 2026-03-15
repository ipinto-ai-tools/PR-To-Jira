"""Configuration management using environment variables."""

from pathlib import Path
from typing import Self

from dotenv import load_dotenv
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """Application configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # GitHub configuration
    github_token: str = Field(..., description="GitHub personal access token")

    # Jira configuration
    jira_base_url: str = Field(..., description="Jira instance base URL")
    jira_email: str | None = Field(None, description="Jira user email")
    jira_user: str | None = Field(None, description="Jira username")
    jira_api_token: str = Field(..., description="Jira API token")

    # Optional configuration
    log_level: str = Field("INFO", description="Logging level")

    @field_validator("jira_base_url")
    @classmethod
    def validate_jira_url(cls, v: str) -> str:
        """Ensure Jira URL doesn't have trailing slash."""
        return v.rstrip("/")

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Ensure log level is valid."""
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"Invalid log level. Must be one of: {valid_levels}")
        return v_upper

    @property
    def jira_auth_user(self) -> str:
        """Return the Jira authentication user (email or username)."""
        return self.jira_email or self.jira_user or ""

    def validate(self) -> None:
        """Validate that required authentication is present."""
        if not self.jira_email and not self.jira_user:
            raise ValueError("Either JIRA_EMAIL or JIRA_USER must be set")

    @classmethod
    def load(cls, env_file: Path | str | None = None) -> Self:
        """
        Load configuration from environment and .env file.

        Args:
            env_file: Optional path to .env file. If None, searches in current directory.

        Returns:
            Configured Config instance.

        Raises:
            ValueError: If required configuration is missing or invalid.
        """
        # Load .env file if it exists
        if env_file:
            load_dotenv(env_file)
        else:
            # Try to find .env in current directory or parent directories
            current = Path.cwd()
            for _ in range(5):  # Search up to 5 levels
                env_path = current / ".env"
                if env_path.exists():
                    load_dotenv(env_path)
                    break
                parent = current.parent
                if parent == current:  # Reached root
                    break
                current = parent

        # Create config instance
        try:
            config = cls()
            config.validate()
            return config
        except Exception as e:
            raise ValueError(f"Configuration error: {e}") from e


def get_config() -> Config:
    """
    Get application configuration.

    Returns:
        Config instance loaded from environment.

    Raises:
        ValueError: If configuration is invalid or missing required values.
    """
    return Config.load()
