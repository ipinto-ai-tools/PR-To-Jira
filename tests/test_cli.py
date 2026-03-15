"""Tests for CLI commands."""

from datetime import datetime
from unittest.mock import Mock

import pytest
from click.testing import CliRunner

from pr_jira_tool.cli import cli
from pr_jira_tool.models import JiraTicket, PRInfo


@pytest.fixture
def runner():
    """Create CLI test runner."""
    return CliRunner()


@pytest.fixture
def mock_env(monkeypatch):
    """Mock environment variables."""
    monkeypatch.setenv("GITHUB_TOKEN", "ghp_test_token")
    monkeypatch.setenv("JIRA_BASE_URL", "https://test.atlassian.net")
    monkeypatch.setenv("JIRA_EMAIL", "test@example.com")
    monkeypatch.setenv("JIRA_API_TOKEN", "test_jira_token")


def test_cli_version(runner):
    """Test CLI version command."""
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.output


def test_review_missing_pr(runner, mock_env):
    """Test review command without PR argument."""
    result = runner.invoke(cli, ["review"])
    assert result.exit_code != 0
    assert "Missing option '--pr'" in result.output


def test_review_dry_run(runner, mock_env, mocker):
    """Test review command with dry-run flag."""
    # Mock PR info
    mock_pr = PRInfo(
        owner="testowner",
        repo="testrepo",
        number=123,
        title="[PROJ-456] Test PR",
        body="Test body",
        branch="main",
        html_url="https://github.com/testowner/testrepo/pull/123",
        state="open",
        labels=["feature"],
        files_changed=["file.py"],
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )

    # Mock Jira ticket
    mock_ticket = JiraTicket(
        key="PROJ-456",
        summary="Test ticket",
        status="Open",
        issue_type="Story",
        project_key="PROJ",
    )

    # Create mock GitHub client
    mock_github_client = Mock()
    mock_github_client.get_pr.return_value = mock_pr
    mock_github_client.has_bot_comment.return_value = False
    mock_github_client.__enter__ = Mock(return_value=mock_github_client)
    mock_github_client.__exit__ = Mock(return_value=None)
    mock_github_client.close = Mock()

    # Create mock Jira client
    mock_jira_client = Mock()
    mock_jira_client.get_ticket.return_value = mock_ticket
    mock_jira_client.has_remote_link.return_value = False
    mock_jira_client.__enter__ = Mock(return_value=mock_jira_client)
    mock_jira_client.__exit__ = Mock(return_value=None)
    mock_jira_client.close = Mock()

    # Patch the client classes
    mocker.patch("pr_jira_tool.cli.GitHubClient", return_value=mock_github_client)
    mocker.patch("pr_jira_tool.cli.JiraClient", return_value=mock_jira_client)

    result = runner.invoke(
        cli,
        [
            "review",
            "--pr",
            "testowner/testrepo#123",
            "--dry-run",
        ],
    )

    assert result.exit_code == 0
    assert "PROJ-456" in result.output


def test_review_with_explicit_jira(runner, mock_env, mocker):
    """Test review with explicitly specified Jira ticket."""
    mock_pr = PRInfo(
        owner="testowner",
        repo="testrepo",
        number=123,
        title="Test PR without ticket in title",
        body="",
        branch="main",
        html_url="https://github.com/testowner/testrepo/pull/123",
        state="open",
        labels=[],
        files_changed=["file.py"],
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )

    mock_ticket = JiraTicket(
        key="PROJ-999",
        summary="Manual ticket",
        status="Open",
        issue_type="Story",
        project_key="PROJ",
    )

    mock_github_client = Mock()
    mock_github_client.get_pr.return_value = mock_pr
    mock_github_client.has_bot_comment.return_value = False
    mock_github_client.__enter__ = Mock(return_value=mock_github_client)
    mock_github_client.__exit__ = Mock(return_value=None)
    mock_github_client.close = Mock()

    mock_jira_client = Mock()
    mock_jira_client.get_ticket.return_value = mock_ticket
    mock_jira_client.has_remote_link.return_value = False
    mock_jira_client.__enter__ = Mock(return_value=mock_jira_client)
    mock_jira_client.__exit__ = Mock(return_value=None)
    mock_jira_client.close = Mock()

    mocker.patch("pr_jira_tool.cli.GitHubClient", return_value=mock_github_client)
    mocker.patch("pr_jira_tool.cli.JiraClient", return_value=mock_jira_client)

    result = runner.invoke(
        cli,
        [
            "review",
            "--pr",
            "testowner/testrepo#123",
            "--jira",
            "PROJ-999",
            "--dry-run",
        ],
    )

    assert result.exit_code == 0
    assert "PROJ-999" in result.output
