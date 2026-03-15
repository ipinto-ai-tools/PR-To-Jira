"""PR summarization and classification logic."""

import re

from pr_jira_tool.jira_client import JiraClient
from pr_jira_tool.models import PRClassification, PRInfo, PRSummary


class PRSummarizer:
    """Summarizes and classifies pull requests."""

    # Classification patterns
    FEATURE_PATTERNS = [
        r"\b(feat|feature|add|implement|introduce)\b",
        r"\bnew\s+\w+",
    ]

    BUG_PATTERNS = [
        r"\b(fix|bug|patch|resolve|correct|repair)\b",
        r"\bissue\s*#?\d+",
    ]

    REFACTOR_PATTERNS = [
        r"\b(refactor|restructure|reorganize|cleanup|clean\s*up)\b",
    ]

    TEST_PATTERNS = [
        r"\b(test|testing|spec|specs)\b",
        r"\.(test|spec)\.",
    ]

    CI_CD_PATTERNS = [
        r"\b(ci|cd|pipeline|workflow|github\s*actions?|jenkins)\b",
        r"\.(github/workflows|\.gitlab-ci|jenkinsfile)",
    ]

    DOCS_PATTERNS = [
        r"\b(doc|docs|documentation|readme)\b",
        r"\.(md|rst|txt)$",
    ]

    CONFIG_PATTERNS = [
        r"\b(config|configuration|settings?)\b",
        r"\.(json|yaml|yml|toml|ini|conf|env)$",
    ]

    DEPENDENCY_PATTERNS = [
        r"\b(dependency|dependencies|upgrade|update.*package|bump)\b",
        r"(package\.json|requirements\.txt|pyproject\.toml|go\.mod|pom\.xml)",
    ]

    DEPLOYMENT_PATTERNS = [
        r"\b(deploy|deployment|release|rollout)\b",
        r"(dockerfile|docker-compose|kubernetes|k8s|helm)",
    ]

    def __init__(self) -> None:
        """Initialize the PR summarizer."""
        pass

    def classify_pr(self, pr_info: PRInfo) -> PRClassification:
        """
        Classify a PR based on title, description, labels, and files.

        Args:
            pr_info: PR information.

        Returns:
            PRClassification enum value.
        """
        # Combine all text for analysis
        text = f"{pr_info.title} {pr_info.body} {pr_info.branch}"
        text_lower = text.lower()

        # Check labels first (most reliable)
        labels_lower = [label.lower() for label in pr_info.labels]
        if any(label in labels_lower for label in ["bug", "fix", "hotfix"]):
            return PRClassification.BUG_FIX
        if any(label in labels_lower for label in ["feature", "enhancement"]):
            return PRClassification.FEATURE
        if "refactor" in labels_lower or "refactoring" in labels_lower:
            return PRClassification.REFACTOR
        if "test" in labels_lower or "tests" in labels_lower:
            return PRClassification.TEST
        if "ci" in labels_lower or "cd" in labels_lower or "ci/cd" in labels_lower:
            return PRClassification.CI_CD
        if "documentation" in labels_lower or "docs" in labels_lower:
            return PRClassification.DOCS
        if "dependencies" in labels_lower or "dependency" in labels_lower:
            return PRClassification.DEPENDENCY

        # Check files (file patterns are strong signals)
        files_text = " ".join(pr_info.files_changed).lower()

        # Test files are a strong signal
        test_count = sum(
            1 for f in pr_info.files_changed if "test" in f.lower() or "spec" in f.lower()
        )
        if test_count / max(len(pr_info.files_changed), 1) > 0.5:
            return PRClassification.TEST

        if self._matches_patterns(files_text, self.CI_CD_PATTERNS):
            return PRClassification.CI_CD

        if self._matches_patterns(files_text, self.DEPLOYMENT_PATTERNS):
            return PRClassification.DEPLOYMENT

        if self._matches_patterns(files_text, self.DEPENDENCY_PATTERNS):
            return PRClassification.DEPENDENCY

        # Check title and description patterns
        if self._matches_patterns(text_lower, self.BUG_PATTERNS):
            return PRClassification.BUG_FIX

        if self._matches_patterns(text_lower, self.REFACTOR_PATTERNS):
            return PRClassification.REFACTOR

        if self._matches_patterns(text_lower, self.DOCS_PATTERNS):
            # Only docs if majority of files are documentation
            doc_count = sum(
                1
                for f in pr_info.files_changed
                if f.endswith((".md", ".rst", ".txt")) or "doc" in f.lower()
            )
            if doc_count / max(len(pr_info.files_changed), 1) > 0.5:
                return PRClassification.DOCS

        if self._matches_patterns(text_lower, self.CONFIG_PATTERNS):
            # Only config if majority of files are config files
            config_count = sum(
                1
                for f in pr_info.files_changed
                if f.endswith((".json", ".yaml", ".yml", ".toml", ".ini", ".conf", ".env"))
            )
            if config_count / max(len(pr_info.files_changed), 1) > 0.5:
                return PRClassification.CONFIG

        if self._matches_patterns(text_lower, self.FEATURE_PATTERNS):
            return PRClassification.FEATURE

        # Default to feature if unclear
        return PRClassification.FEATURE

    def generate_summary(self, pr_info: PRInfo, classification: PRClassification) -> str:
        """
        Generate a descriptive summary of the PR.

        Args:
            pr_info: PR information.
            classification: PR classification.

        Returns:
            Human-readable summary text.
        """
        lines = []

        # Start with title if it's descriptive
        if pr_info.title and len(pr_info.title) > 10:
            lines.append(f"**{pr_info.title}**")
            lines.append("")

        # Add classification context
        classification_context = self._get_classification_context(classification)
        if classification_context:
            lines.append(classification_context)
            lines.append("")

        # Parse body for meaningful content
        if pr_info.body:
            summary_text = self._extract_summary_from_body(pr_info.body)
            if summary_text:
                lines.append(summary_text)
                lines.append("")

        # Add file change summary
        file_summary = self._summarize_files(pr_info.files_changed)
        if file_summary:
            lines.append("**Files Changed:**")
            lines.append(file_summary)
            lines.append("")

        # If we have very little content, add a generic summary
        if len(lines) < 3:
            lines.append(
                f"This PR contains {len(pr_info.files_changed)} file(s) changed "
                f"related to {classification.value}."
            )

        return "\n".join(lines).strip()

    def extract_jira_ticket(self, pr_info: PRInfo) -> str | None:
        """
        Extract Jira ticket ID from PR title, branch, or body.

        Args:
            pr_info: PR information.

        Returns:
            Jira ticket ID if found, None otherwise.
        """
        # Check title first (most common location)
        ticket = JiraClient.extract_ticket_id(pr_info.title)
        if ticket:
            return ticket

        # Check branch name
        ticket = JiraClient.extract_ticket_id(pr_info.branch)
        if ticket:
            return ticket

        # Check body
        ticket = JiraClient.extract_ticket_id(pr_info.body)
        if ticket:
            return ticket

        return None

    def create_summary(self, pr_info: PRInfo, jira_ticket: str | None = None) -> PRSummary:
        """
        Create a complete PR summary with classification.

        Args:
            pr_info: PR information.
            jira_ticket: Optional Jira ticket ID (will auto-detect if not provided).

        Returns:
            PRSummary object.
        """
        classification = self.classify_pr(pr_info)
        summary = self.generate_summary(pr_info, classification)

        # Auto-detect Jira ticket if not provided
        if not jira_ticket:
            jira_ticket = self.extract_jira_ticket(pr_info)

        return PRSummary(
            pr_info=pr_info,
            classification=classification,
            summary=summary,
            jira_ticket=jira_ticket,
        )

    @staticmethod
    def _matches_patterns(text: str, patterns: list[str]) -> bool:
        """Check if text matches any of the regex patterns."""
        return any(re.search(pattern, text, re.IGNORECASE) for pattern in patterns)

    @staticmethod
    def _get_classification_context(classification: PRClassification) -> str:
        """Get contextual description for classification."""
        context_map = {
            PRClassification.FEATURE: "This PR introduces a new feature or enhancement.",
            PRClassification.BUG_FIX: "This PR fixes a bug or issue.",
            PRClassification.REFACTOR: "This PR refactors existing code without changing functionality.",
            PRClassification.TEST: "This PR adds or modifies tests.",
            PRClassification.CI_CD: "This PR updates CI/CD pipelines or workflows.",
            PRClassification.DOCS: "This PR updates documentation.",
            PRClassification.CONFIG: "This PR modifies configuration files.",
            PRClassification.DEPENDENCY: "This PR updates dependencies.",
            PRClassification.DEPLOYMENT: "This PR contains deployment-related changes.",
        }
        return context_map.get(classification, "")

    @staticmethod
    def _extract_summary_from_body(body: str) -> str:
        """Extract meaningful summary text from PR body."""
        if not body:
            return ""

        # Remove HTML comments
        body = re.sub(r"<!--.*?-->", "", body, flags=re.DOTALL)

        # Look for common summary sections
        summary_patterns = [
            r"## Summary\s*\n(.*?)(?:\n##|\n---|\Z)",
            r"## Description\s*\n(.*?)(?:\n##|\n---|\Z)",
            r"## What\s*\n(.*?)(?:\n##|\n---|\Z)",
            r"## Changes\s*\n(.*?)(?:\n##|\n---|\Z)",
        ]

        for pattern in summary_patterns:
            match = re.search(pattern, body, re.IGNORECASE | re.DOTALL)
            if match:
                summary = match.group(1).strip()
                # Clean up the summary
                summary = re.sub(r"\n{3,}", "\n\n", summary)  # Remove excessive newlines
                summary = re.sub(r"^\s*[-*]\s+", "", summary, flags=re.MULTILINE)  # Remove bullets
                if len(summary) > 20:  # Only use if meaningful
                    return summary[:500]  # Limit length

        # If no sections found, use first paragraph
        paragraphs = body.split("\n\n")
        for para in paragraphs:
            para = para.strip()
            # Skip checkbox lists and short lines
            if para and not para.startswith("- [") and len(para) > 50:
                return para[:500]

        return ""

    @staticmethod
    def _summarize_files(files: list[str]) -> str:
        """Create a summary of changed files."""
        if not files:
            return ""

        if len(files) <= 5:
            return "\n".join(f"- `{f}`" for f in files)

        # Group by directory/type
        file_groups: dict[str, list[str]] = {}
        for file in files:
            directory = file.rsplit("/", 1)[0] if "/" in file else "root"

            if directory not in file_groups:
                file_groups[directory] = []
            file_groups[directory].append(file)

        # Summarize groups
        lines = []
        for directory, dir_files in sorted(file_groups.items()):
            if len(dir_files) == 1:
                lines.append(f"- `{dir_files[0]}`")
            else:
                lines.append(f"- `{directory}/`: {len(dir_files)} files")

        return "\n".join(lines[:10])  # Limit to 10 lines
