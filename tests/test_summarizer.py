"""Tests for PR summarizer."""

from datetime import datetime

from pr_jira_tool.models import PRClassification, PRInfo
from pr_jira_tool.summarizer import PRSummarizer


def test_classify_pr_feature_by_label():
    """Test classifying PR as feature based on label."""
    pr = PRInfo(
        owner="test",
        repo="repo",
        number=1,
        title="Add something",
        body="",
        branch="main",
        html_url="https://github.com/test/repo/pull/1",
        state="open",
        labels=["feature"],
        files_changed=["src/file.py"],
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )

    summarizer = PRSummarizer()
    classification = summarizer.classify_pr(pr)
    assert classification == PRClassification.FEATURE


def test_classify_pr_bug_by_label():
    """Test classifying PR as bug fix based on label."""
    pr = PRInfo(
        owner="test",
        repo="repo",
        number=1,
        title="Something",
        body="",
        branch="main",
        html_url="https://github.com/test/repo/pull/1",
        state="open",
        labels=["bug"],
        files_changed=["src/file.py"],
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )

    summarizer = PRSummarizer()
    classification = summarizer.classify_pr(pr)
    assert classification == PRClassification.BUG_FIX


def test_classify_pr_bug_by_title():
    """Test classifying PR as bug fix based on title."""
    pr = PRInfo(
        owner="test",
        repo="repo",
        number=1,
        title="Fix authentication bug",
        body="",
        branch="main",
        html_url="https://github.com/test/repo/pull/1",
        state="open",
        labels=[],
        files_changed=["src/auth.py"],
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )

    summarizer = PRSummarizer()
    classification = summarizer.classify_pr(pr)
    assert classification == PRClassification.BUG_FIX


def test_classify_pr_test_by_files():
    """Test classifying PR as test based on files changed."""
    pr = PRInfo(
        owner="test",
        repo="repo",
        number=1,
        title="Update tests",
        body="",
        branch="main",
        html_url="https://github.com/test/repo/pull/1",
        state="open",
        labels=[],
        files_changed=[
            "tests/test_auth.py",
            "tests/test_user.py",
            "tests/test_api.py",
        ],
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )

    summarizer = PRSummarizer()
    classification = summarizer.classify_pr(pr)
    assert classification == PRClassification.TEST


def test_classify_pr_ci_cd_by_files():
    """Test classifying PR as CI/CD based on files."""
    pr = PRInfo(
        owner="test",
        repo="repo",
        number=1,
        title="Update workflow",
        body="",
        branch="main",
        html_url="https://github.com/test/repo/pull/1",
        state="open",
        labels=[],
        files_changed=[".github/workflows/ci.yml"],
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )

    summarizer = PRSummarizer()
    classification = summarizer.classify_pr(pr)
    assert classification == PRClassification.CI_CD


def test_classify_pr_docs_by_files():
    """Test classifying PR as docs based on files."""
    pr = PRInfo(
        owner="test",
        repo="repo",
        number=1,
        title="Update documentation",
        body="",
        branch="main",
        html_url="https://github.com/test/repo/pull/1",
        state="open",
        labels=[],
        files_changed=["README.md", "docs/guide.md", "docs/api.md"],
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )

    summarizer = PRSummarizer()
    classification = summarizer.classify_pr(pr)
    assert classification == PRClassification.DOCS


def test_classify_pr_config_by_files():
    """Test classifying PR as config based on files."""
    pr = PRInfo(
        owner="test",
        repo="repo",
        number=1,
        title="Update config",
        body="",
        branch="main",
        html_url="https://github.com/test/repo/pull/1",
        state="open",
        labels=[],
        files_changed=["config.yaml", "settings.json"],
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )

    summarizer = PRSummarizer()
    classification = summarizer.classify_pr(pr)
    assert classification == PRClassification.CONFIG


def test_classify_pr_dependency_by_files():
    """Test classifying PR as dependency based on files."""
    pr = PRInfo(
        owner="test",
        repo="repo",
        number=1,
        title="Bump dependencies",
        body="",
        branch="main",
        html_url="https://github.com/test/repo/pull/1",
        state="open",
        labels=[],
        files_changed=["requirements.txt", "package.json"],
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )

    summarizer = PRSummarizer()
    classification = summarizer.classify_pr(pr)
    assert classification == PRClassification.DEPENDENCY


def test_classify_pr_deployment_by_files():
    """Test classifying PR as deployment based on files."""
    pr = PRInfo(
        owner="test",
        repo="repo",
        number=1,
        title="Update deployment",
        body="",
        branch="main",
        html_url="https://github.com/test/repo/pull/1",
        state="open",
        labels=[],
        files_changed=["Dockerfile", "docker-compose.yml"],
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )

    summarizer = PRSummarizer()
    classification = summarizer.classify_pr(pr)
    assert classification == PRClassification.DEPLOYMENT


def test_classify_pr_refactor_by_title():
    """Test classifying PR as refactor based on title."""
    pr = PRInfo(
        owner="test",
        repo="repo",
        number=1,
        title="Refactor authentication module",
        body="",
        branch="main",
        html_url="https://github.com/test/repo/pull/1",
        state="open",
        labels=[],
        files_changed=["src/auth.py"],
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )

    summarizer = PRSummarizer()
    classification = summarizer.classify_pr(pr)
    assert classification == PRClassification.REFACTOR


def test_extract_jira_ticket_from_title():
    """Test extracting Jira ticket from PR title."""
    pr = PRInfo(
        owner="test",
        repo="repo",
        number=1,
        title="[PROJ-123] Add feature",
        body="",
        branch="main",
        html_url="https://github.com/test/repo/pull/1",
        state="open",
        labels=[],
        files_changed=[],
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )

    summarizer = PRSummarizer()
    ticket = summarizer.extract_jira_ticket(pr)
    assert ticket == "PROJ-123"


def test_extract_jira_ticket_from_branch():
    """Test extracting Jira ticket from branch name."""
    pr = PRInfo(
        owner="test",
        repo="repo",
        number=1,
        title="Add feature",
        body="",
        branch="feat/TEAM-456-new-feature",
        html_url="https://github.com/test/repo/pull/1",
        state="open",
        labels=[],
        files_changed=[],
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )

    summarizer = PRSummarizer()
    ticket = summarizer.extract_jira_ticket(pr)
    assert ticket == "TEAM-456"


def test_extract_jira_ticket_from_body():
    """Test extracting Jira ticket from PR body."""
    pr = PRInfo(
        owner="test",
        repo="repo",
        number=1,
        title="Add feature",
        body="This PR fixes ABC-789",
        branch="main",
        html_url="https://github.com/test/repo/pull/1",
        state="open",
        labels=[],
        files_changed=[],
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )

    summarizer = PRSummarizer()
    ticket = summarizer.extract_jira_ticket(pr)
    assert ticket == "ABC-789"


def test_extract_jira_ticket_not_found():
    """Test extracting Jira ticket when none exists."""
    pr = PRInfo(
        owner="test",
        repo="repo",
        number=1,
        title="Add feature",
        body="No ticket here",
        branch="main",
        html_url="https://github.com/test/repo/pull/1",
        state="open",
        labels=[],
        files_changed=[],
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )

    summarizer = PRSummarizer()
    ticket = summarizer.extract_jira_ticket(pr)
    assert ticket is None


def test_generate_summary_with_body():
    """Test generating summary with PR body content."""
    pr = PRInfo(
        owner="test",
        repo="repo",
        number=1,
        title="Add authentication",
        body="## Summary\nThis PR adds OAuth2 authentication support.\n\n## Details\nMore info here",
        branch="main",
        html_url="https://github.com/test/repo/pull/1",
        state="open",
        labels=[],
        files_changed=["src/auth.py"],
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )

    summarizer = PRSummarizer()
    summary = summarizer.generate_summary(pr, PRClassification.FEATURE)

    assert "Add authentication" in summary
    assert "OAuth2 authentication" in summary


def test_generate_summary_without_body():
    """Test generating summary without PR body."""
    pr = PRInfo(
        owner="test",
        repo="repo",
        number=1,
        title="Update code",
        body="",
        branch="main",
        html_url="https://github.com/test/repo/pull/1",
        state="open",
        labels=[],
        files_changed=["file1.py", "file2.py"],
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )

    summarizer = PRSummarizer()
    summary = summarizer.generate_summary(pr, PRClassification.REFACTOR)

    assert len(summary) > 0
    assert "file" in summary.lower()


def test_create_summary():
    """Test creating complete PR summary."""
    pr = PRInfo(
        owner="test",
        repo="repo",
        number=1,
        title="[PROJ-123] Fix bug",
        body="This fixes a critical bug",
        branch="main",
        html_url="https://github.com/test/repo/pull/1",
        state="open",
        labels=["bug"],
        files_changed=["src/file.py"],
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )

    summarizer = PRSummarizer()
    pr_summary = summarizer.create_summary(pr)

    assert pr_summary.pr_info == pr
    assert pr_summary.classification == PRClassification.BUG_FIX
    assert pr_summary.jira_ticket == "PROJ-123"
    assert len(pr_summary.summary) > 0


def test_create_summary_with_explicit_ticket():
    """Test creating summary with explicit Jira ticket."""
    pr = PRInfo(
        owner="test",
        repo="repo",
        number=1,
        title="Add feature",
        body="",
        branch="main",
        html_url="https://github.com/test/repo/pull/1",
        state="open",
        labels=[],
        files_changed=["src/file.py"],
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )

    summarizer = PRSummarizer()
    pr_summary = summarizer.create_summary(pr, jira_ticket="MANUAL-999")

    assert pr_summary.jira_ticket == "MANUAL-999"
