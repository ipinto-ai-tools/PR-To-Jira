"""Pytest fixtures for testing."""

from datetime import datetime

import pytest

from pr_jira_tool.models import PRInfo


@pytest.fixture
def sample_pr_info() -> PRInfo:
    """Create a sample PRInfo object for testing."""
    return PRInfo(
        owner="testowner",
        repo="testrepo",
        number=123,
        title="feat: Add new user authentication",
        body="## Summary\nThis PR adds OAuth2 authentication.\n\n## Changes\n- Added login\n- Added logout",
        branch="feat/PROJ-456-auth",
        html_url="https://github.com/testowner/testrepo/pull/123",
        state="open",
        labels=["feature", "authentication"],
        files_changed=[
            "src/auth/login.py",
            "src/auth/logout.py",
            "tests/test_auth.py",
        ],
        created_at=datetime(2024, 1, 1, 12, 0, 0),
        updated_at=datetime(2024, 1, 2, 12, 0, 0),
    )


@pytest.fixture
def mock_github_client(mocker):
    """Mock GitHub client."""
    client = mocker.Mock()
    client.get_pr = mocker.Mock()
    client.post_comment = mocker.Mock()
    client.get_comments = mocker.Mock(return_value=[])
    client.has_bot_comment = mocker.Mock(return_value=False)
    return client


@pytest.fixture
def mock_jira_client(mocker):
    """Mock Jira client."""
    client = mocker.Mock()
    client.get_ticket = mocker.Mock()
    client.add_remote_link = mocker.Mock()
    client.get_remote_links = mocker.Mock(return_value=[])
    client.has_remote_link = mocker.Mock(return_value=False)
    return client
