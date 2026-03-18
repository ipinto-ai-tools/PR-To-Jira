# PR-to-Jira Tool - How To Guide

Comprehensive guide for configuring and using the PR-to-Jira automation tool.

## Table of Contents

- [Configuration](#configuration)
- [Usage Examples](#usage-examples)
- [Auto-Detection](#auto-detection)
- [Dry Run Mode](#dry-run-mode)
- [Output Formats](#output-formats)
- [CI/CD Integration](#cicd-integration)
- [Troubleshooting](#troubleshooting)
- [Development](#development)

## Configuration

### Environment Variables

Create a `.env` file in the project root with these required variables:

```bash
# GitHub Configuration
GITHUB_TOKEN=ghp_your_github_personal_access_token

# Jira Configuration
JIRA_BASE_URL=https://your-company.atlassian.net
JIRA_EMAIL=your.email@company.com
JIRA_API_TOKEN=your_jira_api_token
```

### Getting API Tokens

#### GitHub Token

1. Go to <https://github.com/settings/tokens>
2. Click "Generate new token (classic)"
3. Select scopes:
   - `repo` - Full control of private repositories
   - `read:org` - Read org and team membership
4. Copy the token (starts with `github_pat`)

#### Jira API Token

1. Go to your Atlassian Cloud account's Security tab: <https://id.atlassian.com/manage-profile/security> (VPN required)
2. Follow the prompts on that screen to generate your token
3. Give it a label (e.g., "PR-to-Jira Tool")
4. Copy the token

### Configuration Validation

Test your configuration with a dry run:

```bash
./pr-jira.sh review --pr owner/repo#1 --dry-run --verbose
```

This will verify credentials without making any changes.

## Usage Examples

### Basic Usage

#### Link PR with Explicit Jira Ticket

```bash
./pr-jira.sh review --pr https://github.com/myorg/myrepo/pull/123 --jira PROJ-456
```

What happens:
1. Fetches PR details from GitHub
2. Analyzes and classifies the PR
3. Generates an intelligent summary
4. Adds a remote link to Jira ticket PROJ-456
5. Posts a summary comment on the PR

#### Short URL Format

```bash
./pr-jira.sh review --pr myorg/myrepo#123 --jira PROJ-456
```

Same as above but with a shorter URL format.

### Supported PR URL Formats

All these formats work:

```bash
# Full URL
--pr https://github.com/owner/repo/pull/123

# Short form
--pr owner/repo#123

# API URL
--pr https://api.github.com/repos/owner/repo/pulls/123
```

## Auto-Detection

The tool can automatically detect Jira ticket IDs from your PR.

### Detection from PR Title

If your PR title is: `[PROJ-789] Add user authentication`

```bash
./pr-jira.sh review --pr myorg/myrepo#123
```

The tool extracts `PROJ-789` automatically.

### Detection from Branch Name

If your branch is: `feat/PROJ-789-user-auth`

```bash
./pr-jira.sh review --pr myorg/myrepo#123
```

The tool extracts `PROJ-789` from the branch name.

### Detection from PR Description

If your PR description contains: `Fixes PROJ-789` or `Relates to PROJ-789`

```bash
./pr-jira.sh review --pr myorg/myrepo#123
```

The tool extracts `PROJ-789` from the PR body.

### Detection Order

The tool searches in this order:
1. PR title
2. Branch name
3. PR description

The first match found is used.

## Dry Run Mode

Preview what the tool will do without making any changes.

### Basic Dry Run

```bash
./pr-jira.sh review --pr myorg/myrepo#123 --dry-run
```

**Output:**

```text
PR Summary for https://github.com/myorg/myrepo/pull/123
========================================

Title: Add user authentication feature
Classification: feature
Jira Ticket: PROJ-456

Summary:
This PR introduces a new user authentication system with OAuth2 support...

DRY RUN - No changes were made

Actions:
○ Would add remote link to Jira ticket
○ Would post summary comment to PR
```

### Verbose Dry Run

See detailed processing information:

```bash
./pr-jira.sh review --pr myorg/myrepo#123 --dry-run --verbose
```

Shows:
- Configuration loading
- API calls being made
- Classification logic
- Summary generation steps

## Output Formats

### Human-Readable (Default)

```bash
./pr-jira.sh review --pr myorg/myrepo#123
```

Produces nicely formatted terminal output with colors and symbols.

### JSON for Automation

```bash
./pr-jira.sh review --pr myorg/myrepo#123 --output json
```

**Sample Output:**

```json
{
  "pr_url": "https://github.com/myorg/myrepo/pull/123",
  "pr_number": 123,
  "title": "Add user authentication feature",
  "classification": "feature",
  "jira_ticket": "PROJ-456",
  "summary": "This PR introduces a new user authentication system...",
  "actions_taken": {
    "linked_to_jira": true,
    "commented_on_pr": true,
    "dry_run": false
  },
  "timestamp": "2024-03-15T10:30:00Z",
  "errors": []
}
```

### JSON with jq

Extract specific fields:

```bash
# Get classification
./pr-jira.sh review --pr myorg/myrepo#123 --output json | jq '.classification'

# Check for errors
./pr-jira.sh review --pr myorg/myrepo#123 --output json | jq '.errors | length'

# Get Jira ticket
./pr-jira.sh review --pr myorg/myrepo#123 --output json | jq -r '.jira_ticket'
```

## Selective Operations

### Link Only (No Comment)

Add a link to Jira without posting a comment to the PR:

```bash
./pr-jira.sh review --pr myorg/myrepo#123 --link-only
```

**Use case:** Track PRs in Jira without cluttering PR discussions.

### Comment Only (No Link)

Post a summary comment to the PR without adding a Jira link:

```bash
./pr-jira.sh review --pr myorg/myrepo#123 --comment-only
```

**Use case:** Automated PR summaries when Jira linking is handled elsewhere.

## CI/CD Integration

### GitHub Actions

Create `.github/workflows/link-pr-to-jira.yml`:

```yaml
name: Link PR to Jira

on:
  pull_request:
    types: [opened, reopened]

jobs:
  link-jira:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Install uv
        run: pip install uv

      - name: Install tool
        run: uv pip install -e .

      - name: Link PR to Jira
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          JIRA_BASE_URL: ${{ secrets.JIRA_BASE_URL }}
          JIRA_EMAIL: ${{ secrets.JIRA_EMAIL }}
          JIRA_API_TOKEN: ${{ secrets.JIRA_API_TOKEN }}
        run: |
          uv run pr-jira review --pr ${{ github.event.pull_request.html_url }} --output json
```

### GitLab CI

Create or update `.gitlab-ci.yml`:

```yaml
link-to-jira:
  stage: review
  image: python:3.12
  script:
    - pip install uv
    - uv pip install -e .
    - uv run pr-jira review --pr $CI_MERGE_REQUEST_URL --output json
  only:
    - merge_requests
  variables:
    GITHUB_TOKEN: $GITHUB_TOKEN
    JIRA_BASE_URL: $JIRA_BASE_URL
    JIRA_EMAIL: $JIRA_EMAIL
    JIRA_API_TOKEN: $JIRA_API_TOKEN
```

### Bulk Processing

Process multiple PRs:

```bash
#!/bin/bash
PRS=(
  "myorg/myrepo#123"
  "myorg/myrepo#124"
  "myorg/myrepo#125"
)

for pr in "${PRS[@]}"; do
  echo "Processing $pr..."
  ./pr-jira.sh review --pr "$pr" --output json || echo "Failed: $pr"
done
```

## Troubleshooting

### Common Errors

#### "GITHUB_TOKEN not set"

**Problem:** Environment variables not loaded.

**Solution:**
- Ensure `.env` file exists in project root
- Use `./pr-jira.sh` wrapper script (loads `.env` automatically)
- Or manually load: `source .env` before running

#### "Failed to fetch PR"

**Problem:** Cannot access the PR from GitHub.

**Solutions:**
- Verify PR URL format (see supported formats above)
- Check GitHub token has `repo` scope
- Confirm PR exists and you have read access
- Test token: `curl -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user`

#### "Jira ticket not found"

**Problem:** Cannot find or access the Jira ticket.

**Solutions:**
- Verify ticket ID format (e.g., PROJ-123, not just 123)
- Check Jira base URL ends with `.atlassian.net`
- Ensure API token has read/write access to the project
- Test Jira access: Check you can view the ticket in your browser

#### "No Jira ticket found in PR"

**Problem:** Auto-detection failed.

**Solutions:**
- Add ticket ID to PR title: `[PROJ-123] Feature name`
- Add ticket ID to branch name: `feat/PROJ-123-description`
- Add ticket reference to PR body: `Fixes PROJ-123`
- Or specify explicitly: `--jira PROJ-123`

### Idempotency Check

The tool is safe to run multiple times:

```bash
# First run - creates link and comment
./pr-jira.sh review --pr myorg/myrepo#123

# Second run - detects existing link and comment, skips
./pr-jira.sh review --pr myorg/myrepo#123
```

**Output:**

```text
○ Link already exists on Jira ticket
○ Comment already exists on PR
```

### Verbose Debugging

Enable detailed logging:

```bash
./pr-jira.sh review --pr myorg/myrepo#123 --verbose
```

Shows:
- Configuration loading
- API calls and responses
- Classification decisions
- Summary generation process
- Errors with full stack traces

### Error Handling in Scripts

Handle errors gracefully:

```bash
#!/bin/bash
set -e

if ./pr-jira.sh review --pr "$1" --output json > result.json 2>&1; then
  echo "Success!"
  jq '.summary' result.json
else
  echo "Failed with errors:"
  jq '.errors' result.json
  exit 1
fi
```

## Development

### Setting Up Development Environment

1. **Clone and install**

   ```bash
   git clone <repository-url>
   cd Jira_updater
   uv pip install -e ".[dev]"
   ```

2. **Configure environment**

   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

3. **Verify installation**

   ```bash
   uv run pytest
   ```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=pr_jira_tool --cov-report=html

# Run specific test file
uv run pytest tests/test_cli.py

# Run specific test
uv run pytest tests/test_cli.py::test_review_dry_run
```

### Code Quality

```bash
# Format code
uvx ruff format .

# Check formatting
uvx ruff format --check .

# Lint code
uvx ruff check .

# Auto-fix linting issues
uvx ruff check --fix .

# Type checking
uvx mypy pr_jira_tool/
```

### Using the Makefile

The project includes convenient make targets:

```bash
make test          # Run all tests
make test-cov      # Run tests with coverage report
make format        # Format code with ruff
make lint          # Lint code
make typecheck     # Type check with mypy
make clean         # Clean build artifacts
```

## Tips and Best Practices

### 1. Always Test First

Use dry run before making real changes:

```bash
./pr-jira.sh review --pr myorg/myrepo#123 --dry-run
```

### 2. Leverage Auto-Detection

Include Jira ticket IDs in PR titles or branch names:

```bash
# Good PR title
[PROJ-123] Add feature

# Good branch name
feat/PROJ-123-add-feature
```

### 3. Use JSON in Automation

In scripts and CI/CD pipelines:

```bash
./pr-jira.sh review --pr "$PR_URL" --output json | jq '.jira_ticket'
```

### 4. Set Appropriate Log Levels

For production:

```bash
export LOG_LEVEL=WARNING
```

For debugging:

```bash
export LOG_LEVEL=DEBUG
./pr-jira.sh review --pr myorg/myrepo#123 --verbose
```

### 5. Validate Credentials Early

Test credentials before bulk operations:

```bash
./pr-jira.sh review --pr myorg/myrepo#123 --dry-run
```

This fails fast if credentials are invalid.

## Security Best Practices

- Never commit `.env` files or tokens to version control
- The `.gitignore` automatically excludes `.env`
- Rotate tokens regularly
- Use minimal required permissions:
  - GitHub: `repo` scope for private repos
  - Jira: Write access only to relevant projects
- Store secrets in CI/CD secret management (GitHub Secrets, GitLab Variables, etc.)

## PR Classification Details

The tool classifies PRs into these categories:

| Type | Detection Criteria |
|------|-------------------|
| **feature** | Labels: feature, enhancement<br>Keywords: feat, add, implement, introduce |
| **bug fix** | Labels: bug, fix<br>Keywords: fix, bug, resolve, patch |
| **refactor** | Label: refactor<br>Keywords: refactor, cleanup, restructure |
| **test** | 50%+ test files changed<br>Keywords: test, testing |
| **CI/CD** | Changes to `.github/workflows/`, `.gitlab-ci.yml`, Jenkinsfile |
| **docs** | 50%+ `.md` or `.rst` files<br>Keywords: docs, documentation |
| **config** | 50%+ `.json`, `.yaml`, `.toml`, `.ini` files |
| **dependency** | Changes to `requirements.txt`, `package.json`, `go.mod`, etc. |
| **deployment** | Changes to deployment manifests or infrastructure files |

Classification uses:
1. PR labels (highest priority)
2. File patterns and extensions
3. PR title and description keywords
4. File change percentages

## Advanced Workflows

### Scheduled Reviews

Review all open PRs daily:

```bash
#!/bin/bash
# review-open-prs.sh

# Get all open PRs (using gh CLI)
prs=$(gh pr list --repo myorg/myrepo --state open --json number --jq '.[].number')

for number in $prs; do
  ./pr-jira.sh review --pr "myorg/myrepo#$number" --link-only
done
```

Add to cron:

```bash
# Daily at 9 AM
0 9 * * * /path/to/review-open-prs.sh
```

### Conditional Linking

Only link if PR matches certain criteria:

```bash
#!/bin/bash
PR_URL=$1
BRANCH=$(gh pr view $PR_URL --json headRefName --jq '.headRefName')

if [[ $BRANCH =~ ^(feat|fix)/ ]]; then
  ./pr-jira.sh review --pr "$PR_URL"
else
  echo "Skipping: branch $BRANCH doesn't match pattern"
fi
```

### Slack Notification Integration

```bash
#!/bin/bash
RESULT=$(./pr-jira.sh review --pr "$PR_URL" --output json)
TICKET=$(echo "$RESULT" | jq -r '.jira_ticket')
CLASSIFICATION=$(echo "$RESULT" | jq -r '.classification')

curl -X POST $SLACK_WEBHOOK_URL \
  -H 'Content-Type: application/json' \
  -d "{\"text\": \"PR linked to $TICKET (type: $CLASSIFICATION)\"}"
```

## Getting Help

1. Check this guide for usage patterns
2. Use `--help` for command reference: `./pr-jira.sh review --help`
3. Enable `--verbose` for detailed debugging
4. Check test files in `tests/` for API usage examples
5. Open a GitHub issue for bugs or feature requests
