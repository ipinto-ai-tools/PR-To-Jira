"""Tests for Jira client."""

import httpx

from pr_jira_tool.jira_client import JiraClient


def test_extract_ticket_id():
    """Test extracting Jira ticket ID from text."""
    assert JiraClient.extract_ticket_id("Fix PROJ-123 bug") == "PROJ-123"
    assert JiraClient.extract_ticket_id("[TEAM-456] Add feature") == "TEAM-456"
    assert JiraClient.extract_ticket_id("feat/ABC-789-description") == "ABC-789"
    assert JiraClient.extract_ticket_id("No ticket here") is None


def test_extract_ticket_id_multiple():
    """Test extracting first ticket when multiple exist."""
    text = "Related to PROJ-123 and PROJ-456"
    assert JiraClient.extract_ticket_id(text) == "PROJ-123"


def test_get_ticket(mocker):
    """Test fetching Jira ticket information."""
    mock_client = mocker.Mock()
    ticket_response = mocker.Mock()
    ticket_response.json.return_value = {
        "key": "PROJ-123",
        "fields": {
            "summary": "Test ticket",
            "status": {"name": "In Progress"},
            "issuetype": {"name": "Story"},
            "project": {"key": "PROJ"},
        },
    }
    ticket_response.raise_for_status = mocker.Mock()
    mock_client.get = mocker.Mock(return_value=ticket_response)

    client = JiraClient("https://test.atlassian.net", "test@example.com", "token")
    client._client = mock_client

    ticket = client.get_ticket("PROJ-123")

    assert ticket.key == "PROJ-123"
    assert ticket.summary == "Test ticket"
    assert ticket.status == "In Progress"
    assert ticket.issue_type == "Story"
    assert ticket.project_key == "PROJ"


def test_add_remote_link(mocker):
    """Test adding remote link to Jira ticket."""
    mock_client = mocker.Mock()
    link_response = mocker.Mock()
    link_response.json.return_value = {"id": 1, "self": "https://..."}
    link_response.raise_for_status = mocker.Mock()
    mock_client.post = mocker.Mock(return_value=link_response)

    client = JiraClient("https://test.atlassian.net", "test@example.com", "token")
    client._client = mock_client

    result = client.add_remote_link(
        "PROJ-123",
        "https://github.com/owner/repo/pull/1",
        "PR #1: Test PR",
    )

    assert result["id"] == 1
    mock_client.post.assert_called_once()


def test_get_remote_links(mocker):
    """Test getting remote links from Jira ticket."""
    mock_client = mocker.Mock()
    links_response = mocker.Mock()
    links_response.json.return_value = [
        {"object": {"url": "https://github.com/owner/repo/pull/1"}},
        {"object": {"url": "https://github.com/owner/repo/pull/2"}},
    ]
    links_response.raise_for_status = mocker.Mock()
    mock_client.get = mocker.Mock(return_value=links_response)

    client = JiraClient("https://test.atlassian.net", "test@example.com", "token")
    client._client = mock_client

    links = client.get_remote_links("PROJ-123")

    assert len(links) == 2


def test_has_remote_link_true(mocker):
    """Test checking for existing remote link."""
    mock_client = mocker.Mock()
    links_response = mocker.Mock()
    links_response.json.return_value = [
        {"object": {"url": "https://github.com/owner/repo/pull/1"}},
        {"object": {"url": "https://github.com/owner/repo/pull/2"}},
    ]
    links_response.raise_for_status = mocker.Mock()
    mock_client.get = mocker.Mock(return_value=links_response)

    client = JiraClient("https://test.atlassian.net", "test@example.com", "token")
    client._client = mock_client

    assert client.has_remote_link("PROJ-123", "https://github.com/owner/repo/pull/1") is True


def test_has_remote_link_false(mocker):
    """Test checking for non-existent remote link."""
    mock_client = mocker.Mock()
    links_response = mocker.Mock()
    links_response.json.return_value = [
        {"object": {"url": "https://github.com/owner/repo/pull/1"}},
    ]
    links_response.raise_for_status = mocker.Mock()
    mock_client.get = mocker.Mock(return_value=links_response)

    client = JiraClient("https://test.atlassian.net", "test@example.com", "token")
    client._client = mock_client

    assert client.has_remote_link("PROJ-123", "https://github.com/owner/repo/pull/999") is False


def test_has_remote_link_error(mocker):
    """Test has_remote_link returns False on error."""
    mock_client = mocker.Mock()
    mock_client.get = mocker.Mock(side_effect=httpx.HTTPError("Error"))

    client = JiraClient("https://test.atlassian.net", "test@example.com", "token")
    client._client = mock_client

    assert client.has_remote_link("PROJ-123", "https://github.com/owner/repo/pull/1") is False


def test_add_comment(mocker):
    """Test adding comment to Jira ticket."""
    mock_client = mocker.Mock()
    comment_response = mocker.Mock()
    comment_response.json.return_value = {"id": "123"}
    comment_response.raise_for_status = mocker.Mock()
    mock_client.post = mocker.Mock(return_value=comment_response)

    client = JiraClient("https://test.atlassian.net", "test@example.com", "token")
    client._client = mock_client

    result = client.add_comment("PROJ-123", "Test comment")

    assert result["id"] == "123"
    mock_client.post.assert_called_once()


def test_context_manager(mocker):
    """Test using client as context manager."""
    client = JiraClient("https://test.atlassian.net", "test@example.com", "token")
    mock_close = mocker.patch.object(client, "close")

    with client as c:
        assert c is client

    mock_close.assert_called_once()
