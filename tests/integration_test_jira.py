#!/usr/bin/env python3
"""
Integration test for Jira client against real Jira API.

This script requires valid Jira credentials in the .env file:
- JIRA_BASE_URL
- JIRA_EMAIL
- JIRA_API_TOKEN

Usage:
    uv run tests/integration_test_jira.py [TICKET_KEY]

Example:
    uv run tests/integration_test_jira.py BUILD-1739
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

from pr_jira_tool.jira_client import JiraClient


def test_jira_connection(ticket_key: str) -> None:
    """
    Test Jira client against real API.

    Args:
        ticket_key: Jira ticket key to test with (e.g., BUILD-1739).
    """
    # Load environment variables
    env_path = project_root / ".env"
    if not env_path.exists():
        print(f"ERROR: .env file not found at {env_path}")
        print("Please create a .env file with Jira credentials.")
        sys.exit(1)

    load_dotenv(env_path)

    # Get credentials
    base_url = os.getenv("JIRA_BASE_URL")
    email = os.getenv("JIRA_EMAIL")
    api_token = os.getenv("JIRA_API_TOKEN")

    # Validate credentials
    missing = []
    if not base_url:
        missing.append("JIRA_BASE_URL")
    if not email:
        missing.append("JIRA_EMAIL")
    if not api_token:
        missing.append("JIRA_API_TOKEN")

    if missing:
        print(f"ERROR: Missing required environment variables: {', '.join(missing)}")
        print("Please check your .env file.")
        sys.exit(1)

    print(f"Testing Jira connection...")
    print(f"  Base URL: {base_url}")
    print(f"  Email: {email}")
    print(f"  Ticket: {ticket_key}")
    print()

    try:
        # Create client
        with JiraClient(base_url, email, api_token) as client:
            # Test 1: Fetch ticket
            print(f"[TEST 1] Fetching ticket {ticket_key}...")
            try:
                ticket = client.get_ticket(ticket_key)
                print(f"  ✓ Success!")
                print(f"    Key: {ticket.key}")
                print(f"    Summary: {ticket.summary}")
                print(f"    Status: {ticket.status}")
                print(f"    Type: {ticket.issue_type}")
                print(f"    Project: {ticket.project_key}")
                print()
            except Exception as e:
                print(f"  ✗ Failed: {e}")
                print()
                raise

            # Test 2: Get remote links
            print(f"[TEST 2] Getting remote links for {ticket_key}...")
            try:
                links = client.get_remote_links(ticket_key)
                print(f"  ✓ Success!")
                print(f"    Found {len(links)} remote link(s)")
                for i, link in enumerate(links, 1):
                    link_obj = link.get("object", {})
                    url = link_obj.get("url", "N/A")
                    title = link_obj.get("title", "N/A")
                    print(f"    {i}. {title}")
                    print(f"       URL: {url}")
                print()
            except Exception as e:
                print(f"  ✗ Failed: {e}")
                print()
                raise

            # Test 3: Check for specific remote link
            test_url = "https://github.com/example/test/pull/1"
            print(f"[TEST 3] Checking if remote link exists...")
            print(f"  URL: {test_url}")
            try:
                exists = client.has_remote_link(ticket_key, test_url)
                print(f"  ✓ Success!")
                print(f"    Link exists: {exists}")
                print()
            except Exception as e:
                print(f"  ✗ Failed: {e}")
                print()
                raise

        print("=" * 60)
        print("All tests passed!")
        print("=" * 60)

    except Exception as e:
        print("=" * 60)
        print(f"Integration test failed: {e}")
        print("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    # Get ticket key from command line or use default
    ticket_key = sys.argv[1] if len(sys.argv) > 1 else "BUILD-1739"
    test_jira_connection(ticket_key)
