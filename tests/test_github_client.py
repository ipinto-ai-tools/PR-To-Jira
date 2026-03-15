"""Tests for GitHub client."""

import pytest

from pr_jira_tool.github_client import GitHubClient


def test_parse_pr_url_full():
    """Test parsing full GitHub PR URL."""
    owner, repo, number = GitHubClient.parse_pr_url(
        "https://github.com/testowner/testrepo/pull/123"
    )
    assert owner == "testowner"
    assert repo == "testrepo"
    assert number == 123


def test_parse_pr_url_short():
    """Test parsing short PR reference."""
    owner, repo, number = GitHubClient.parse_pr_url("testowner/testrepo#123")
    assert owner == "testowner"
    assert repo == "testrepo"
    assert number == 123


def test_parse_pr_url_invalid():
    """Test parsing invalid PR URL."""
    with pytest.raises(ValueError, match="Invalid PR URL format"):
        GitHubClient.parse_pr_url("invalid-url")


def test_parse_pr_url_without_protocol():
    """Test parsing URL without protocol."""
    owner, repo, number = GitHubClient.parse_pr_url("github.com/testowner/testrepo/pull/456")
    assert owner == "testowner"
    assert repo == "testrepo"
    assert number == 456


def test_fetch_pr(mocker):
    """Test fetching PR information."""
    mock_client = mocker.Mock()

    # Mock PR response
    pr_data = {
        "title": "Test PR",
        "body": "Test body",
        "head": {"ref": "test-branch"},
        "html_url": "https://github.com/owner/repo/pull/1",
        "state": "open",
        "labels": [{"name": "bug"}, {"name": "feature"}],
        "created_at": "2024-01-01T12:00:00Z",
        "updated_at": "2024-01-02T12:00:00Z",
    }

    pr_response = mocker.Mock()
    pr_response.json.return_value = pr_data
    pr_response.raise_for_status = mocker.Mock()

    # Mock files response
    files_data = [
        {"filename": "file1.py"},
        {"filename": "file2.py"},
    ]

    files_response = mocker.Mock()
    files_response.json.return_value = files_data
    files_response.raise_for_status = mocker.Mock()

    mock_client.get = mocker.Mock(side_effect=[pr_response, files_response])

    # Create client and patch _client
    client = GitHubClient("test_token")
    client._client = mock_client

    # Fetch PR
    pr_info = client._fetch_pr("owner", "repo", 1)

    assert pr_info.owner == "owner"
    assert pr_info.repo == "repo"
    assert pr_info.number == 1
    assert pr_info.title == "Test PR"
    assert pr_info.body == "Test body"
    assert pr_info.branch == "test-branch"
    assert pr_info.state == "open"
    assert pr_info.labels == ["bug", "feature"]
    assert pr_info.files_changed == ["file1.py", "file2.py"]


def test_post_comment(mocker):
    """Test posting a comment to PR."""
    mock_client = mocker.Mock()
    comment_response = mocker.Mock()
    comment_response.json.return_value = {"id": 123, "body": "Test comment"}
    comment_response.raise_for_status = mocker.Mock()
    mock_client.post = mocker.Mock(return_value=comment_response)

    client = GitHubClient("test_token")
    client._client = mock_client

    result = client.post_comment("owner", "repo", 1, "Test comment")

    assert result["id"] == 123
    mock_client.post.assert_called_once()


def test_get_comments(mocker):
    """Test getting PR comments."""
    mock_client = mocker.Mock()
    comments_response = mocker.Mock()
    comments_response.json.return_value = [
        {"id": 1, "body": "Comment 1"},
        {"id": 2, "body": "Comment 2"},
    ]
    comments_response.raise_for_status = mocker.Mock()
    mock_client.get = mocker.Mock(return_value=comments_response)

    client = GitHubClient("test_token")
    client._client = mock_client

    comments = client.get_comments("owner", "repo", 1)

    assert len(comments) == 2
    assert comments[0]["body"] == "Comment 1"


def test_has_bot_comment_true(mocker):
    """Test checking for bot comment when it exists."""
    mock_client = mocker.Mock()
    comments_response = mocker.Mock()
    comments_response.json.return_value = [
        {"body": "Regular comment"},
        {"body": "Some text *This summary was automatically generated.* more text"},
    ]
    comments_response.raise_for_status = mocker.Mock()
    mock_client.get = mocker.Mock(return_value=comments_response)

    client = GitHubClient("test_token")
    client._client = mock_client

    assert client.has_bot_comment("owner", "repo", 1) is True


def test_has_bot_comment_false(mocker):
    """Test checking for bot comment when it doesn't exist."""
    mock_client = mocker.Mock()
    comments_response = mocker.Mock()
    comments_response.json.return_value = [
        {"body": "Regular comment"},
        {"body": "Another comment"},
    ]
    comments_response.raise_for_status = mocker.Mock()
    mock_client.get = mocker.Mock(return_value=comments_response)

    client = GitHubClient("test_token")
    client._client = mock_client

    assert client.has_bot_comment("owner", "repo", 1) is False


def test_context_manager(mocker):
    """Test using client as context manager."""
    client = GitHubClient("test_token")
    mock_close = mocker.patch.object(client, "close")

    with client as c:
        assert c is client

    mock_close.assert_called_once()
