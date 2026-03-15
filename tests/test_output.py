"""Tests for output formatting."""

from datetime import datetime

from pr_jira_tool.models import OperationResult
from pr_jira_tool.output import OutputFormatter


def test_print_human_output():
    """Test human-readable output format."""
    formatter = OutputFormatter(verbose=False)
    result = OperationResult(
        pr_url="https://github.com/test/repo/pull/1",
        pr_number=1,
        title="Test PR",
        classification="feature",
        jira_ticket="PROJ-123",
        summary="Test summary",
        linked_to_jira=True,
        commented_on_pr=True,
        dry_run=False,
        timestamp=datetime.now(),
        errors=None,
    )

    # Just ensure it doesn't crash
    formatter.print_result(result)


def test_print_human_output_with_errors():
    """Test human-readable output with errors."""
    formatter = OutputFormatter(verbose=False)
    result = OperationResult(
        pr_url="https://github.com/test/repo/pull/1",
        pr_number=1,
        title="Test PR",
        classification="feature",
        jira_ticket="PROJ-123",
        summary="Test summary",
        linked_to_jira=False,
        commented_on_pr=False,
        dry_run=False,
        timestamp=datetime.now(),
        errors=["Error 1", "Error 2"],
    )

    # Just ensure it doesn't crash
    formatter.print_result(result)


def test_print_dry_run_output():
    """Test dry-run output format."""
    formatter = OutputFormatter(verbose=False)
    result = OperationResult(
        pr_url="https://github.com/test/repo/pull/1",
        pr_number=1,
        title="Test PR",
        classification="feature",
        jira_ticket="PROJ-123",
        summary="Test summary",
        linked_to_jira=False,
        commented_on_pr=False,
        dry_run=True,
        timestamp=datetime.now(),
        errors=None,
    )

    # Just ensure it doesn't crash
    formatter.print_result(result)


def test_print_info_verbose():
    """Test verbose info messages."""
    formatter = OutputFormatter(verbose=True)
    # Just ensure it doesn't crash
    formatter.print_info("Test info message")


def test_print_info_not_verbose(capsys):
    """Test that info messages are hidden when not verbose."""
    formatter = OutputFormatter(verbose=False)
    formatter.print_info("Test info message")
    captured = capsys.readouterr()
    # Output should be empty when not verbose
    assert captured.out == ""


def test_print_success():
    """Test success messages."""
    formatter = OutputFormatter(verbose=False)
    # Just ensure it doesn't crash
    formatter.print_success("Test success")


def test_print_warning():
    """Test warning messages."""
    formatter = OutputFormatter(verbose=False)
    # Just ensure it doesn't crash
    formatter.print_warning("Test warning")


def test_print_error():
    """Test error messages."""
    formatter = OutputFormatter(verbose=False)
    # Just ensure it doesn't crash
    formatter.print_error("Test error")
