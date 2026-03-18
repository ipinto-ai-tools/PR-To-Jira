# Integration Tests

This directory contains both unit tests and integration tests for the pr-jira-tool.

## Unit Tests

The unit tests use mocking and don't require any external API credentials:

```bash
# Run all unit tests
uv run pytest tests/

# Run with coverage
uv run pytest tests/ --cov=pr_jira_tool --cov-report=term-missing
```

## Integration Tests

Integration tests run against the real Jira API and require valid credentials.

### Prerequisites

1. Configure your `.env` file with real Jira credentials:
   ```bash
   JIRA_BASE_URL=https://redhat.atlassian.net
   JIRA_EMAIL=your.email@company.com
   JIRA_API_TOKEN=your_api_token_here
   ```

2. Ensure you have access to a valid Jira ticket for testing.

### Running Integration Tests

#### Jira Client Integration Test

Test the Jira API connection and basic operations:

```bash
# Test with specific ticket
uv run --with python-dotenv tests/integration_test_jira.py BUILD-1739

# Test with different ticket
uv run --with python-dotenv tests/integration_test_jira.py YOUR-TICKET-123
```

The integration test performs these operations:
1. Fetches ticket information
2. Retrieves remote links
3. Checks for link existence

#### Expected Output

```
Testing Jira connection...  
[TEST 1] Fetching ticket BUILD-1739...
  ✓ Success!
    Key: BUILD-1739
    Summary: Run Shared Resource tests in Konflux
    Status: To Do
    Type: Story
    Project: BUILD

[TEST 2] Getting remote links for BUILD-1739...
  ✓ Success!
    Found 3 remote link(s)
    ...

[TEST 3] Checking if remote link exists...
  ✓ Success!
    Link exists: False

============================================================
All tests passed!
============================================================
```

### Troubleshooting

**Authentication Errors (401)**
- Verify your `JIRA_API_TOKEN` is correct and not expired
- Check that `JIRA_EMAIL` matches the account associated with the token

**Permission Errors (403)**
- Ensure your Jira account has permission to view the ticket
- Verify you have access to the project (e.g., BUILD project)

**Not Found Errors (404)**
- Check that the ticket ID is correct and exists
- Verify `JIRA_BASE_URL` points to the correct Jira instance

**Network Errors**
- Confirm you have network access to the Jira instance
- Check if VPN is required for access

### Security Note

Integration tests use real API credentials from your `.env` file. Never commit the `.env` file or expose credentials in test output or version control.
