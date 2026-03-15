"""Tests for configuration management."""

import pytest

from pr_jira_tool.config import Config


def test_config_with_email(monkeypatch):
    """Test configuration with Jira email."""
    monkeypatch.setenv("GITHUB_TOKEN", "ghp_test_token")
    monkeypatch.setenv("JIRA_BASE_URL", "https://test.atlassian.net/")
    monkeypatch.setenv("JIRA_EMAIL", "test@example.com")
    monkeypatch.setenv("JIRA_API_TOKEN", "jira_token")

    config = Config()
    assert config.github_token == "ghp_test_token"
    assert config.jira_base_url == "https://test.atlassian.net"  # Trailing slash removed
    assert config.jira_email == "test@example.com"
    assert config.jira_api_token == "jira_token"
    assert config.jira_auth_user == "test@example.com"


def test_config_with_user(monkeypatch):
    """Test configuration with Jira username."""
    monkeypatch.setenv("GITHUB_TOKEN", "ghp_test_token")
    monkeypatch.setenv("JIRA_BASE_URL", "https://test.atlassian.net")
    monkeypatch.setenv("JIRA_USER", "testuser")
    monkeypatch.setenv("JIRA_API_TOKEN", "jira_token")

    config = Config()
    assert config.jira_user == "testuser"
    assert config.jira_auth_user == "testuser"


def test_config_missing_auth_fails(monkeypatch):
    """Test that missing both email and user fails validation."""
    monkeypatch.setenv("GITHUB_TOKEN", "ghp_test_token")
    monkeypatch.setenv("JIRA_BASE_URL", "https://test.atlassian.net")
    monkeypatch.setenv("JIRA_API_TOKEN", "jira_token")

    config = Config()
    with pytest.raises(ValueError, match="Either JIRA_EMAIL or JIRA_USER must be set"):
        config.validate()


def test_config_log_level_validation(monkeypatch):
    """Test log level validation."""
    monkeypatch.setenv("GITHUB_TOKEN", "token")
    monkeypatch.setenv("JIRA_BASE_URL", "https://test.atlassian.net")
    monkeypatch.setenv("JIRA_EMAIL", "test@example.com")
    monkeypatch.setenv("JIRA_API_TOKEN", "token")
    monkeypatch.setenv("LOG_LEVEL", "debug")

    config = Config()
    assert config.log_level == "DEBUG"


def test_config_invalid_log_level(monkeypatch):
    """Test invalid log level."""
    monkeypatch.setenv("GITHUB_TOKEN", "token")
    monkeypatch.setenv("JIRA_BASE_URL", "https://test.atlassian.net")
    monkeypatch.setenv("JIRA_EMAIL", "test@example.com")
    monkeypatch.setenv("JIRA_API_TOKEN", "token")
    monkeypatch.setenv("LOG_LEVEL", "INVALID")

    with pytest.raises(ValueError):
        Config()


def test_config_missing_required_field(monkeypatch):
    """Test missing required field."""
    monkeypatch.setenv("JIRA_BASE_URL", "https://test.atlassian.net")
    monkeypatch.setenv("JIRA_EMAIL", "test@example.com")
    monkeypatch.setenv("JIRA_API_TOKEN", "token")
    # Missing GITHUB_TOKEN

    with pytest.raises(Exception):  # Pydantic validation error
        Config()


def test_jira_url_trailing_slash_removed(monkeypatch):
    """Test that trailing slash is removed from Jira URL."""
    monkeypatch.setenv("GITHUB_TOKEN", "token")
    monkeypatch.setenv("JIRA_BASE_URL", "https://test.atlassian.net///")
    monkeypatch.setenv("JIRA_EMAIL", "test@example.com")
    monkeypatch.setenv("JIRA_API_TOKEN", "token")

    config = Config()
    assert config.jira_base_url == "https://test.atlassian.net"
