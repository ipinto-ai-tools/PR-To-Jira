"""Command-line interface for PR-to-Jira tool."""

import sys
from datetime import datetime

import click
import httpx

from pr_jira_tool.config import get_config
from pr_jira_tool.github_client import GitHubClient
from pr_jira_tool.jira_client import JiraClient
from pr_jira_tool.models import OperationResult
from pr_jira_tool.output import OutputFormatter
from pr_jira_tool.summarizer import PRSummarizer


@click.group()
@click.version_option(version="0.1.0")
def cli() -> None:
    """PR-to-Jira automation tool for linking GitHub PRs with Jira tickets."""
    pass


@cli.command()
@click.option(
    "--pr",
    required=True,
    help="PR URL or short reference (e.g., owner/repo#123)",
)
@click.option(
    "--jira",
    "jira_ticket",
    default=None,
    help="Jira ticket ID (e.g., PROJ-123). Auto-detected if not provided.",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Preview changes without applying them",
)
@click.option(
    "--comment-only",
    is_flag=True,
    help="Only add comment to PR (skip Jira link)",
)
@click.option(
    "--link-only",
    is_flag=True,
    help="Only add Jira link (skip PR comment)",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose output",
)
def review(
    pr: str,
    jira_ticket: str | None,
    dry_run: bool,
    comment_only: bool,
    link_only: bool,
    verbose: bool,
) -> None:
    """
    Review a PR and link it to a Jira ticket with an intelligent summary.

    Examples:

        # Basic usage with explicit Jira ticket
        pr-jira review --pr https://github.com/owner/repo/pull/123 --jira PROJ-456

        # Auto-detect Jira ticket from PR
        pr-jira review --pr owner/repo#123

        # Dry run to preview changes
        pr-jira review --pr owner/repo#123 --dry-run

        # Only add Jira link
        pr-jira review --pr owner/repo#123 --link-only
    """
    formatter = OutputFormatter(verbose=verbose)
    errors: list[str] = []

    try:
        # Load configuration
        formatter.print_info("Loading configuration...")
        config = get_config()

        # Initialize clients
        formatter.print_info("Initializing API clients...")
        github = GitHubClient(config.github_token)
        jira = JiraClient(
            config.jira_base_url,
            config.jira_auth_user,
            config.jira_api_token,
        )

        # Fetch PR information
        formatter.print_info(f"Fetching PR information from {pr}...")
        try:
            pr_info = github.get_pr(pr)
        except ValueError as e:
            formatter.print_error(str(e))
            sys.exit(1)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                formatter.print_error(f"PR not found: {pr}")
            else:
                formatter.print_error(f"GitHub API error: {e}")
            sys.exit(1)

        formatter.print_success(f"Found PR: {pr_info.title}")

        # Create summary
        formatter.print_info("Analyzing PR and generating summary...")
        summarizer = PRSummarizer()
        summary = summarizer.create_summary(pr_info, jira_ticket)

        # Validate Jira ticket
        if not summary.jira_ticket:
            formatter.print_error(
                "No Jira ticket found in PR title, branch, or body. Please specify --jira TICKET-ID"
            )
            sys.exit(1)

        formatter.print_info(f"Detected Jira ticket: {summary.jira_ticket}")

        # Verify Jira ticket exists (skip in dry-run mode)
        if not dry_run:
            try:
                ticket_info = jira.get_ticket(summary.jira_ticket)
                formatter.print_success(f"Jira ticket found: {ticket_info.summary}")
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    formatter.print_error(f"Jira ticket not found: {summary.jira_ticket}")
                else:
                    formatter.print_error(f"Jira API error: {e}")
                sys.exit(1)
        else:
            formatter.print_info("[DRY RUN] Skipping Jira ticket validation")

        # Track actions taken
        linked_to_jira = False
        commented_on_pr = False

        # Add Jira link (unless comment-only)
        if not comment_only:
            link_exists = jira.has_remote_link(summary.jira_ticket, pr_info.html_url)

            if link_exists:
                formatter.print_info("Remote link already exists on Jira ticket")
            elif dry_run:
                formatter.print_info(f"[DRY RUN] Would add remote link to {summary.jira_ticket}")
            else:
                formatter.print_info(f"Adding remote link to {summary.jira_ticket}...")
                try:
                    jira.add_remote_link(
                        summary.jira_ticket,
                        pr_info.html_url,
                        f"PR #{pr_info.number}: {pr_info.title}",
                        "https://github.githubassets.com/favicons/favicon.png",
                    )
                    linked_to_jira = True
                    formatter.print_success("Remote link added successfully")
                except httpx.HTTPError as e:
                    error_msg = f"Failed to add Jira link: {e}"
                    errors.append(error_msg)
                    formatter.print_error(error_msg)

        # Add PR comment (unless link-only)
        if not link_only:
            comment_exists = github.has_bot_comment(pr_info.owner, pr_info.repo, pr_info.number)

            if comment_exists:
                formatter.print_info("Summary comment already exists on PR")
            elif dry_run:
                formatter.print_info("[DRY RUN] Would post summary comment to PR")
                if verbose:
                    formatter.console.print("\n[bold]Comment Preview:[/bold]")
                    formatter.console.print(summary.to_comment())
            else:
                formatter.print_info("Posting summary comment to PR...")
                try:
                    github.post_comment(
                        pr_info.owner,
                        pr_info.repo,
                        pr_info.number,
                        summary.to_comment(),
                    )
                    commented_on_pr = True
                    formatter.print_success("Comment posted successfully")
                except httpx.HTTPError as e:
                    error_msg = f"Failed to post PR comment: {e}"
                    errors.append(error_msg)
                    formatter.print_error(error_msg)

        # Create operation result
        result = OperationResult(
            pr_url=pr_info.html_url,
            pr_number=pr_info.number,
            title=pr_info.title,
            classification=summary.classification.value,
            jira_ticket=summary.jira_ticket,
            summary=summary.summary,
            linked_to_jira=linked_to_jira,
            commented_on_pr=commented_on_pr,
            dry_run=dry_run,
            timestamp=datetime.now(),
            errors=errors if errors else None,
        )

        # Print result
        formatter.print_result(result)

        # Close clients
        github.close()
        jira.close()

        # Exit with error if there were errors
        if errors:
            sys.exit(1)

    except ValueError as e:
        formatter.print_error(f"Configuration error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        formatter.print_warning("\nOperation cancelled by user")
        sys.exit(130)
    except Exception as e:
        formatter.print_error(f"Unexpected error: {e}")
        if verbose:
            raise
        sys.exit(1)


def main() -> None:
    """Entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
