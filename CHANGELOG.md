# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-03-15

### Added

- Initial release of PR-to-Jira automation tool
- GitHub PR metadata extraction (title, description, files, diff, labels, reviewers)
- Automatic Jira ticket ID detection from PR title, branch name, or description
- PR classification system (feature, bug fix, refactor, test, CI/CD, docs, config, dependency, deployment)
- Intelligent PR summary generation
- Jira remote link creation to associate PRs with tickets
- PR comment posting with structured summaries
- Idempotent operations (safe to run multiple times)
- Dry-run mode for previewing changes
- JSON and human-readable output formats
- Selective operations (link-only, comment-only)
- Comprehensive test suite with 80%+ coverage
- CLI interface using Click framework
- Environment-based configuration with .env support
- Wrapper script (pr-jira.sh) for easy execution

### Technical Features

- Python 3.12+ support
- Type hints throughout codebase
- Pydantic models for data validation
- httpx for async HTTP operations
- Modular architecture with clear separation of concerns
- Rich console output with colors and formatting
- Comprehensive error handling and logging
- Development tools: pytest, ruff, mypy

[0.1.0]: https://github.com/yourusername/Jira_updater/releases/tag/v0.1.0
