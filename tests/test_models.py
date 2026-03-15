"""Tests for data models."""

from datetime import datetime

from pr_jira_tool.models import (
    PRClassification,
    PRInfo,
    PRSummary,
)


def test_pr_info_full_name():
    """Test PRInfo.full_name property."""
    pr = PRInfo(
        owner="testowner",
        repo="testrepo",
        number=123,
        title="Test PR",
        body="",
        branch="main",
        html_url="https://github.com/testowner/testrepo/pull/123",
        state="open",
        labels=[],
        files_changed=[],
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    assert pr.full_name == "testowner/testrepo"


def test_pr_info_short_ref():
    """Test PRInfo.short_ref property."""
    pr = PRInfo(
        owner="testowner",
        repo="testrepo",
        number=123,
        title="Test PR",
        body="",
        branch="main",
        html_url="https://github.com/testowner/testrepo/pull/123",
        state="open",
        labels=[],
        files_changed=[],
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    assert pr.short_ref == "testowner/testrepo#123"


def test_pr_summary_to_comment():
    """Test PRSummary.to_comment formatting."""
    pr = PRInfo(
        owner="test",
        repo="repo",
        number=1,
        title="Test",
        body="",
        branch="main",
        html_url="https://github.com/test/repo/pull/1",
        state="open",
        labels=[],
        files_changed=[],
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )

    summary = PRSummary(
        pr_info=pr,
        classification=PRClassification.FEATURE,
        summary="This is a test summary",
        jira_ticket="PROJ-123",
    )

    comment = summary.to_comment()
    assert "## PR Summary" in comment
    assert "**Classification:** feature" in comment
    assert "**Jira Ticket:** PROJ-123" in comment
    assert "This is a test summary" in comment
    assert "*This summary was automatically generated.*" in comment


def test_pr_summary_to_comment_no_jira():
    """Test PRSummary.to_comment without Jira ticket."""
    pr = PRInfo(
        owner="test",
        repo="repo",
        number=1,
        title="Test",
        body="",
        branch="main",
        html_url="https://github.com/test/repo/pull/1",
        state="open",
        labels=[],
        files_changed=[],
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )

    summary = PRSummary(
        pr_info=pr,
        classification=PRClassification.BUG_FIX,
        summary="Bug fix summary",
        jira_ticket=None,
    )

    comment = summary.to_comment()
    assert "**Jira Ticket:**" not in comment
    assert "**Classification:** bug fix" in comment
