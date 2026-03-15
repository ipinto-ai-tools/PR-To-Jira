# PR-to-Jira Automation Tool

A Python CLI tool that automatically links GitHub Pull Requests to Jira tickets with intelligent summaries and classification.

## Overview

This tool bridges the gap between GitHub pull requests and Jira issue tracking by:

- Extracting PR information from GitHub (title, description, files, diff, labels)
- Auto-detecting Jira ticket IDs from PR title, branch name, or description
- Classifying PRs (feature, bug fix, refactor, test, CI/CD, docs, etc.)
- Linking PRs to Jira tickets via remote links
- Posting descriptive summaries as PR comments

The tool is **idempotent** - safe to run multiple times without creating duplicates.

## Quick Start

### 1. Install Dependencies

```bash
# Using uv (recommended)
uv pip install -e .

# Or using pip
pip install -e .
```

### 2. Configure Credentials

Create a `.env` file:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```bash
GITHUB_TOKEN=ghp_your_github_token_here
JIRA_BASE_URL=https://your-company.atlassian.net
JIRA_EMAIL=your.email@company.com
JIRA_API_TOKEN=your_jira_api_token_here
```

**Where to get tokens:**
- GitHub: https://github.com/settings/tokens (needs `repo` scope)
- Jira: https://id.atlassian.com/manage-profile/security/api-tokens

### 3. Run the Tool

```bash
# Using the wrapper script (loads .env automatically)
./pr-jira.sh review --pr https://github.com/owner/repo/pull/123

# Or directly with uv
uv run pr-jira review --pr https://github.com/owner/repo/pull/123
```

## Basic Usage

```bash
# Auto-detect Jira ticket from PR
./pr-jira.sh review --pr owner/repo#123

# Specify Jira ticket explicitly
./pr-jira.sh review --pr owner/repo#123 --jira PROJ-456

# Preview changes without applying them
./pr-jira.sh review --pr owner/repo#123 --dry-run
```

## Common Options

| Option | Description |
|--------|-------------|
| `--dry-run` | Preview changes without applying them |
| `--link-only` | Only add Jira link (no PR comment) |
| `--comment-only` | Only add PR comment (no Jira link) |
| `--verbose` | Show detailed logging |
| `--output json` | Output structured JSON (for automation) |

## How It Works

1. Fetches PR details from GitHub
2. Detects Jira ticket ID (from title, branch, or description)
3. Classifies the PR type based on files, labels, and keywords
4. Generates an intelligent summary
5. Creates a remote link in Jira
6. Posts a summary comment on the PR

## PR Classifications

The tool automatically classifies PRs into these types:

- **feature** - New features or enhancements
- **bug fix** - Bug fixes
- **refactor** - Code restructuring
- **test** - Test additions/modifications
- **CI/CD** - Pipeline changes
- **docs** - Documentation updates
- **config** - Configuration changes
- **dependency** - Dependency updates
- **deployment** - Deployment changes

Classification uses PR labels, file patterns, and keywords from titles/descriptions.

## Need More Help?

See **HOWTO.md** for:
- Detailed configuration
- Advanced usage examples
- Troubleshooting
- Development setup
- CI/CD integration

## Requirements

- Python 3.12+
- uv package manager (https://docs.astral.sh/uv/getting-started/installation/)
- GitHub and Jira API tokens

## Project Structure

```text
Jira_updater/
├── pr_jira_tool/           # Main package
│   ├── cli.py              # CLI entry point
│   ├── config.py           # Configuration management
│   ├── github_client.py    # GitHub API client
│   ├── jira_client.py      # Jira API client
│   ├── models.py           # Data models
│   ├── output.py           # Output formatting
│   └── summarizer.py       # PR summary generation
├── tests/                  # Test suite
├── pr-jira.sh             # Wrapper script (loads .env)
├── pyproject.toml         # Python project configuration
├── README.md              # This file
├── HOWTO.md              # Detailed usage guide
└── .env.example          # Example environment variables
```

## License

MIT License - See LICENSE file for details
