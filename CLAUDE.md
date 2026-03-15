# PR-to-Jira Automation Tool

## Project Overview

A production-ready Python CLI tool that bridges GitHub pull requests with Jira ticket tracking. The tool extracts PR metadata, generates concise summaries of changes, and updates Jira tickets with PR links and readable summaries for full traceability.

**What this tool does:**

- Reads GitHub pull request metadata (title, body, author, files, diff, state, labels, reviewers)
- Generates concise, descriptive summaries of what the PR is doing
- Classifies PRs by type (feature, bug fix, refactor, test, CI/CD, docs, config, dependency, deployment)
- Updates Jira tickets with PR link (using remote link API)
- Posts readable summary as PR comment

**What this tool does NOT do:**

- Code review (that's handled by external tools like Qodo)
- Quality assessment or evaluation
- PR approval/rejection

## Core Behavior

### Summary Generation

The tool produces **descriptive** summaries, not evaluative ones:

- Focus on WHAT changed, not HOW GOOD it is
- Classify PR type based on labels, file patterns, and keywords
- Extract key files modified and their purpose
- Identify dependencies added/removed
- Note breaking changes if documented

**Good summary example:**
> "Adds user authentication middleware using JWT tokens. Introduces new `auth/` module with token validation, user session management, and role-based access control. Updates API endpoints to require authentication. Migration script included for user roles table."

**Bad summary example (evaluative):**
> "Well-structured authentication implementation. Good separation of concerns. Could improve error handling."

### Jira Integration

**Remote Link Addition:**

- Use Jira remote link API to associate PR with ticket
- Check for existing link to avoid duplicates (idempotent)
- Include PR title, URL, and status

**Comment Posting:**

- Post formatted comment with PR summary
- Include metadata: author, reviewers, file count, line changes
- Check for existing identical comment to avoid duplicates (idempotent)

### Ticket Extraction

If Jira ticket ID not explicitly provided, extract from:

1. PR title (e.g., `[PROJ-123] Add feature`)
2. Branch name (e.g., `feature/PROJ-123-description`)
3. PR body (look for `Jira: PROJ-123` or similar patterns)

If no ticket found, exit with clear error message.

## Technical Standards

### Code Quality

- Python 3.12+
- Type hints for all public functions
- Docstrings (Google or NumPy style) for all public classes/functions
- Use `mypy` for static type checking
- Use `ruff` for code formatting and linting

### Architecture

Modular design with clear separation of concerns:

- **`cli.py`** - CLI interface and orchestration
- **`config.py`** - Configuration management (environment variables, settings)
- **`github_client.py`** - GitHub API interactions
- **`jira_client.py`** - Jira API interactions
- **`summarizer.py`** - PR summary generation and classification
- **`models.py`** - Data models (PR, Jira ticket, etc.)
- **`output.py`** - Output formatting (console, JSON)

Key principles:

- Testable components (dependency injection for API clients)
- Configuration via environment variables
- Secrets management (never hardcode tokens)

### Error Handling

- Robust error handling for all API calls
- Clear, actionable error messages
- Graceful degradation where possible
- Retry logic with exponential backoff for transient failures
- Log full context for debugging
- Sensitive data (tokens) never logged

### Testing

- Unit tests for all business logic
- Integration tests for API clients (with mocking)
- Pytest as test framework
- Aim for 80%+ code coverage
- Test edge cases (missing data, API failures, duplicate operations)

### Operational Features

- **Dry-run mode**: Preview actions without making changes
- **Idempotent operations**: Safe to run multiple times
- **Exit codes**: 0 for success, non-zero for errors
- **Progress indicators**: Clear feedback during execution
- **Multiple output formats**: Human-readable and JSON

## Project Structure

```text
Jira_updater/
├── pr_jira_tool/              # Main package
│   ├── __init__.py
│   ├── __main__.py            # Entry point for python -m
│   ├── cli.py                 # CLI interface (Click)
│   ├── config.py              # Configuration management
│   ├── github_client.py       # GitHub API client
│   ├── jira_client.py         # Jira API client
│   ├── models.py              # Data models (Pydantic)
│   ├── output.py              # Output formatting
│   └── summarizer.py          # PR summary generation
├── tests/                     # Test suite
│   ├── __init__.py
│   ├── test_cli.py
│   ├── test_github_client.py
│   ├── test_jira_client.py
│   ├── test_summarizer.py
│   └── fixtures/              # Test data
├── pr-jira.sh                 # Wrapper script (loads .env)
├── pyproject.toml             # Python project config
├── Makefile                   # Development shortcuts
├── README.md                  # User documentation
├── HOWTO.md                   # Detailed guide
├── CLAUDE.md                  # This file
└── .env.example               # Example environment variables
```

## CLI Interface

### Command Structure

```bash
pr-jira review --pr <PR_URL> [OPTIONS]
```

### Required Arguments

- `--pr` - PR URL or short form (e.g., `owner/repo#123`)

### Optional Arguments

- `--jira TICKET_ID` - Jira ticket ID (auto-detected if not provided)
- `--dry-run` - Preview without making changes
- `--verbose` / `-v` - Increase logging verbosity
- `--link-only` - Don't add comment (link only)
- `--comment-only` - Don't add link (comment only)
- `--output FORMAT` - Output format (`text` or `json`)

### Environment Variables

Required:

- `GITHUB_TOKEN` - GitHub personal access token
- `JIRA_BASE_URL` - Jira instance URL (e.g., `https://company.atlassian.net`)
- `JIRA_EMAIL` - Jira email address
- `JIRA_API_TOKEN` - Jira API token

Optional:

- `LOG_LEVEL` - Logging level (DEBUG, INFO, WARNING, ERROR)

### Example Usage

```bash
# Basic usage (ticket extracted from PR)
pr-jira review --pr https://github.com/org/repo/pull/123

# Explicit ticket ID
pr-jira review --pr org/repo#123 --jira PROJ-456

# Dry run
pr-jira review --pr org/repo#123 --dry-run

# Verbose logging
pr-jira review --pr org/repo#123 --verbose

# JSON output for automation
pr-jira review --pr org/repo#123 --output json
```

## Security Best Practices

- Never commit tokens or credentials
- Use `.env` file locally (excluded from git via `.gitignore`)
- Validate all inputs (PR URLs, ticket IDs)
- Use HTTPS for all API calls
- Limit token permissions to minimum required:
  - GitHub: `repo` scope for private repos, `public_repo` for public
  - Jira: Write access to relevant projects only

## Development Workflow

### Development Setup

```bash
# Clone repository
git clone <repository-url>
cd Jira_updater

# Install dependencies
uv pip install -e ".[dev]"

# Configure environment
cp .env.example .env
# Edit .env with your credentials
```

### Testing

```bash
# Run tests
uv run pytest

# Check coverage
uv run pytest --cov=pr_jira_tool --cov-report=html

# Type check
uvx mypy pr_jira_tool

# Lint
uvx ruff check pr_jira_tool
```

### Before Commit

```bash
# Format code
uvx ruff format pr_jira_tool tests

# Run full test suite
make test

# Update documentation if needed
```

### Using Make Targets

```bash
make test          # Run all tests
make test-cov      # Run tests with coverage report
make format        # Format code with ruff
make lint          # Lint code
make typecheck     # Type check with mypy
make clean         # Clean build artifacts
```

## Known Limitations

- Summary generation uses rule-based approach (consider LLM integration for richer summaries)
- Single PR per invocation (no batch mode yet)
- English-only summaries

## Potential Enhancements

- Batch processing of multiple PRs
- Support for other VCS (GitLab, Bitbucket)
- Support for other issue trackers (Linear, Azure DevOps)
- Webhook mode (trigger on PR events)
- Summary customization via templates
- Metrics export (Prometheus, StatsD)

## Troubleshooting

### Common Issues

**Issue:** "Jira ticket not found in PR"

**Solution:** Explicitly pass `--jira PROJ-123` or ensure PR title/branch includes ticket ID

**Issue:** "GitHub API rate limit exceeded"

**Solution:** Use authenticated token, wait for rate limit reset

**Issue:** "Duplicate comments on Jira"

**Solution:** Check idempotency logic - should detect existing comments

**Issue:** "Permission denied on Jira"

**Solution:** Verify API token has write access to the project

### Debugging

Enable verbose logging:

```bash
pr-jira review --pr <url> --verbose
```

Check logs for:

- API request/response details
- Extracted metadata
- Generated summary
- Jira operations attempted

## Support & Contribution

For questions, issues, or contributions:

- Check README.md for usage documentation
- Check HOWTO.md for detailed examples
- Run tests to verify changes: `make test`
- Follow code style: `make format lint typecheck`
