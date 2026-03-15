"""Main entry point for the PR Jira Tool CLI."""

import os
import sys

import click
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@click.group()
@click.version_option(version="1.0.0")
def main():
    """PR Jira Tool - CLI for syncing GitHub PRs with Jira tickets."""
    # Validate required environment variables
    required_vars = ["GITHUB_TOKEN", "JIRA_BASE_URL", "JIRA_API_TOKEN"]
    missing = [var for var in required_vars if not os.getenv(var)]

    if missing and not any(arg in sys.argv for arg in ["--help", "--version"]):
        click.echo(f"Error: Missing required environment variables: {', '.join(missing)}", err=True)
        click.echo("\nPlease set the following environment variables:", err=True)
        click.echo("  - GITHUB_TOKEN", err=True)
        click.echo("  - JIRA_BASE_URL", err=True)
        click.echo("  - JIRA_EMAIL (or JIRA_USER)", err=True)
        click.echo("  - JIRA_API_TOKEN", err=True)
        sys.exit(1)


@main.command()
@click.option("--pr", required=True, help="GitHub PR URL")
@click.option("--jira", required=True, help="Jira ticket ID (e.g., PROJ-123)")
@click.option("--verbose", is_flag=True, help="Enable verbose output")
def review(pr, jira, verbose):
    """Review a GitHub PR and update Jira ticket."""
    if verbose:
        click.echo(f"Processing PR: {pr}")
        click.echo(f"Jira ticket: {jira}")

    try:
        # Placeholder for actual implementation
        click.echo(f"✓ Successfully synced PR {pr} with Jira ticket {jira}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@main.command()
def config():
    """Show current configuration."""
    click.echo("Current Configuration:")
    click.echo(f"  GITHUB_TOKEN: {'✓ Set' if os.getenv('GITHUB_TOKEN') else '✗ Not set'}")
    click.echo(f"  JIRA_BASE_URL: {os.getenv('JIRA_BASE_URL', '✗ Not set')}")
    click.echo(f"  JIRA_EMAIL: {os.getenv('JIRA_EMAIL', '✗ Not set')}")
    click.echo(f"  JIRA_USER: {os.getenv('JIRA_USER', '✗ Not set')}")
    click.echo(f"  JIRA_API_TOKEN: {'✓ Set' if os.getenv('JIRA_API_TOKEN') else '✗ Not set'}")


if __name__ == "__main__":
    main()
