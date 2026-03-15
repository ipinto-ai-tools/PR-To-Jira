"""Data models for PR and Jira entities."""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class PRClassification(StrEnum):
    """PR classification categories."""

    FEATURE = "feature"
    BUG_FIX = "bug fix"
    REFACTOR = "refactor"
    TEST = "test"
    CI_CD = "CI/CD"
    DOCS = "docs"
    CONFIG = "config"
    DEPENDENCY = "dependency"
    DEPLOYMENT = "deployment"


@dataclass(frozen=True, slots=True)
class PRInfo:
    """GitHub Pull Request information."""

    owner: str
    repo: str
    number: int
    title: str
    body: str
    branch: str
    html_url: str
    state: str
    labels: list[str]
    files_changed: list[str]
    created_at: datetime
    updated_at: datetime

    @property
    def full_name(self) -> str:
        """Return the full repository name."""
        return f"{self.owner}/{self.repo}"

    @property
    def short_ref(self) -> str:
        """Return short reference like 'owner/repo#123'."""
        return f"{self.owner}/{self.repo}#{self.number}"


@dataclass(frozen=True, slots=True)
class JiraTicket:
    """Jira ticket information."""

    key: str
    summary: str
    status: str
    issue_type: str
    project_key: str

    @property
    def project(self) -> str:
        """Extract project key from ticket key."""
        return self.key.split("-")[0]


@dataclass(frozen=True, slots=True)
class PRSummary:
    """Summary and classification of a PR."""

    pr_info: PRInfo
    classification: PRClassification
    summary: str
    jira_ticket: str | None = None

    def to_comment(self) -> str:
        """Generate a formatted comment for posting to the PR."""
        lines = [
            "## PR Summary",
            "",
            f"**Classification:** {self.classification.value}",
        ]

        if self.jira_ticket:
            lines.append(f"**Jira Ticket:** {self.jira_ticket}")

        lines.extend(
            [
                "",
                "### Summary",
                self.summary,
                "",
                "---",
                "*This summary was automatically generated.*",
            ]
        )

        return "\n".join(lines)


@dataclass(frozen=True, slots=True)
class OperationResult:
    """Result of PR-to-Jira operation."""

    pr_url: str
    pr_number: int
    title: str
    classification: str
    jira_ticket: str | None
    summary: str
    linked_to_jira: bool
    commented_on_pr: bool
    dry_run: bool
    timestamp: datetime
    errors: list[str] | None = None
