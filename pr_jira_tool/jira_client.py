"""Jira API client for managing tickets and links."""

import re
from typing import Any

import httpx

from pr_jira_tool.models import JiraTicket


class JiraClient:
    """Client for interacting with the Jira API."""

    TICKET_PATTERN = re.compile(r"\b([A-Z][A-Z0-9]+-\d+)\b")

    def __init__(self, base_url: str, email: str, api_token: str, timeout: float = 30.0) -> None:
        """
        Initialize Jira client.

        Args:
            base_url: Jira instance base URL (e.g., https://company.atlassian.net).
            email: Jira user email or username.
            api_token: Jira API token.
            timeout: Request timeout in seconds.
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._client = httpx.Client(
            base_url=f"{self.base_url}/rest/api/3",
            auth=(email, api_token),
            headers={"Accept": "application/json", "Content-Type": "application/json"},
            timeout=timeout,
        )

    def __enter__(self) -> "JiraClient":
        """Context manager entry."""
        return self

    def __exit__(self, *args: Any) -> None:
        """Context manager exit."""
        self.close()

    def close(self) -> None:
        """Close the HTTP client."""
        self._client.close()

    @staticmethod
    def extract_ticket_id(text: str) -> str | None:
        """
        Extract Jira ticket ID from text.

        Args:
            text: Text to search for ticket ID.

        Returns:
            First ticket ID found, or None if no match.
        """
        match = JiraClient.TICKET_PATTERN.search(text)
        return match.group(1) if match else None

    def get_ticket(self, ticket_key: str) -> JiraTicket:
        """
        Fetch Jira ticket information.

        Args:
            ticket_key: Jira ticket key (e.g., PROJ-123).

        Returns:
            JiraTicket object.

        Raises:
            httpx.HTTPError: If API request fails.
        """
        response = self._client.get(
            f"/issue/{ticket_key}", params={"fields": "summary,status,issuetype,project"}
        )
        response.raise_for_status()
        data = response.json()

        return JiraTicket(
            key=data["key"],
            summary=data["fields"]["summary"],
            status=data["fields"]["status"]["name"],
            issue_type=data["fields"]["issuetype"]["name"],
            project_key=data["fields"]["project"]["key"],
        )

    def add_remote_link(
        self, ticket_key: str, url: str, title: str, icon_url: str | None = None
    ) -> dict[str, Any]:
        """
        Add a remote link to a Jira ticket.

        Args:
            ticket_key: Jira ticket key.
            url: URL to link.
            title: Link title/description.
            icon_url: Optional icon URL.

        Returns:
            Link data from API response.

        Raises:
            httpx.HTTPError: If API request fails.
        """
        payload: dict[str, Any] = {
            "object": {
                "url": url,
                "title": title,
            }
        }

        if icon_url:
            payload["object"]["icon"] = {"url16x16": icon_url}

        response = self._client.post(
            f"/issue/{ticket_key}/remotelink",
            json=payload,
        )
        response.raise_for_status()
        return response.json()

    def get_remote_links(self, ticket_key: str) -> list[dict[str, Any]]:
        """
        Get all remote links for a Jira ticket.

        Args:
            ticket_key: Jira ticket key.

        Returns:
            List of remote link data dictionaries.

        Raises:
            httpx.HTTPError: If API request fails.
        """
        response = self._client.get(f"/issue/{ticket_key}/remotelink")
        response.raise_for_status()
        return response.json()

    def has_remote_link(self, ticket_key: str, url: str) -> bool:
        """
        Check if a remote link already exists on a Jira ticket.

        Args:
            ticket_key: Jira ticket key.
            url: URL to check.

        Returns:
            True if link exists, False otherwise.
        """
        try:
            links = self.get_remote_links(ticket_key)
            return any(link.get("object", {}).get("url") == url for link in links)
        except httpx.HTTPError:
            return False

    def add_comment(self, ticket_key: str, body: str) -> dict[str, Any]:
        """
        Add a comment to a Jira ticket.

        Args:
            ticket_key: Jira ticket key.
            body: Comment body text.

        Returns:
            Comment data from API response.

        Raises:
            httpx.HTTPError: If API request fails.
        """
        # Jira uses ADF (Atlassian Document Format) for comments
        payload = {
            "body": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": body}],
                    }
                ],
            }
        }

        response = self._client.post(
            f"/issue/{ticket_key}/comment",
            json=payload,
        )
        response.raise_for_status()
        return response.json()
