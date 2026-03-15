"""GitHub API client for fetching PR information."""

import re
from datetime import datetime
from typing import Any

import httpx

from pr_jira_tool.models import PRInfo


class GitHubClient:
    """Client for interacting with the GitHub API."""

    API_BASE = "https://api.github.com"
    PR_URL_PATTERN = re.compile(r"(?:https?://)?(?:www\.)?github\.com/([^/]+)/([^/]+)/pull/(\d+)")
    SHORT_REF_PATTERN = re.compile(r"([^/]+)/([^/#]+)#(\d+)")

    def __init__(self, token: str, timeout: float = 30.0) -> None:
        """
        Initialize GitHub client.

        Args:
            token: GitHub personal access token.
            timeout: Request timeout in seconds.
        """
        self.token = token
        self.timeout = timeout
        self._client = httpx.Client(
            base_url=self.API_BASE,
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
            timeout=timeout,
        )

    def __enter__(self) -> "GitHubClient":
        """Context manager entry."""
        return self

    def __exit__(self, *args: Any) -> None:
        """Context manager exit."""
        self.close()

    def close(self) -> None:
        """Close the HTTP client."""
        self._client.close()

    @staticmethod
    def parse_pr_url(pr_url: str) -> tuple[str, str, int]:
        """
        Parse PR URL into owner, repo, and number.

        Args:
            pr_url: PR URL in various formats.

        Returns:
            Tuple of (owner, repo, pr_number).

        Raises:
            ValueError: If URL format is invalid.
        """
        # Try full URL format
        match = GitHubClient.PR_URL_PATTERN.match(pr_url)
        if match:
            owner, repo, pr_num = match.groups()
            return owner, repo, int(pr_num)

        # Try short format (owner/repo#123)
        match = GitHubClient.SHORT_REF_PATTERN.match(pr_url)
        if match:
            owner, repo, pr_num = match.groups()
            return owner, repo, int(pr_num)

        raise ValueError(
            f"Invalid PR URL format: {pr_url}. "
            "Expected formats: "
            "https://github.com/owner/repo/pull/123 or owner/repo#123"
        )

    def get_pr(self, pr_url: str) -> PRInfo:
        """
        Fetch PR information from GitHub.

        Args:
            pr_url: PR URL or short reference.

        Returns:
            PRInfo object with PR details.

        Raises:
            ValueError: If PR URL is invalid.
            httpx.HTTPError: If API request fails.
        """
        owner, repo, pr_number = self.parse_pr_url(pr_url)
        return self._fetch_pr(owner, repo, pr_number)

    def _fetch_pr(self, owner: str, repo: str, pr_number: int) -> PRInfo:
        """
        Fetch PR information from GitHub API.

        Args:
            owner: Repository owner.
            repo: Repository name.
            pr_number: PR number.

        Returns:
            PRInfo object.

        Raises:
            httpx.HTTPError: If API request fails.
        """
        # Fetch PR data
        pr_response = self._client.get(f"/repos/{owner}/{repo}/pulls/{pr_number}")
        pr_response.raise_for_status()
        pr_data = pr_response.json()

        # Fetch files changed
        files_response = self._client.get(f"/repos/{owner}/{repo}/pulls/{pr_number}/files")
        files_response.raise_for_status()
        files_data = files_response.json()

        return PRInfo(
            owner=owner,
            repo=repo,
            number=pr_number,
            title=pr_data["title"],
            body=pr_data.get("body") or "",
            branch=pr_data["head"]["ref"],
            html_url=pr_data["html_url"],
            state=pr_data["state"],
            labels=[label["name"] for label in pr_data.get("labels", [])],
            files_changed=[f["filename"] for f in files_data],
            created_at=datetime.fromisoformat(pr_data["created_at"].replace("Z", "+00:00")),
            updated_at=datetime.fromisoformat(pr_data["updated_at"].replace("Z", "+00:00")),
        )

    def post_comment(self, owner: str, repo: str, pr_number: int, body: str) -> dict[str, Any]:
        """
        Post a comment to a PR.

        Args:
            owner: Repository owner.
            repo: Repository name.
            pr_number: PR number.
            body: Comment body in Markdown.

        Returns:
            Comment data from API response.

        Raises:
            httpx.HTTPError: If API request fails.
        """
        response = self._client.post(
            f"/repos/{owner}/{repo}/issues/{pr_number}/comments",
            json={"body": body},
        )
        response.raise_for_status()
        return response.json()

    def get_comments(self, owner: str, repo: str, pr_number: int) -> list[dict[str, Any]]:
        """
        Get all comments on a PR.

        Args:
            owner: Repository owner.
            repo: Repository name.
            pr_number: PR number.

        Returns:
            List of comment data dictionaries.

        Raises:
            httpx.HTTPError: If API request fails.
        """
        response = self._client.get(f"/repos/{owner}/{repo}/issues/{pr_number}/comments")
        response.raise_for_status()
        return response.json()

    def has_bot_comment(self, owner: str, repo: str, pr_number: int) -> bool:
        """
        Check if PR already has an auto-generated summary comment.

        Args:
            owner: Repository owner.
            repo: Repository name.
            pr_number: PR number.

        Returns:
            True if bot comment exists, False otherwise.
        """
        comments = self.get_comments(owner, repo, pr_number)
        marker = "*This summary was automatically generated.*"
        return any(marker in comment.get("body", "") for comment in comments)
