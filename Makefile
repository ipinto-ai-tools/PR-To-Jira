.PHONY: help install install-dev test test-cov lint format typecheck clean run

help:
	@echo "Available commands:"
	@echo "  make install      - Install package"
	@echo "  make install-dev  - Install package with dev dependencies"
	@echo "  make test         - Run tests"
	@echo "  make test-cov     - Run tests with coverage report"
	@echo "  make lint         - Run linter"
	@echo "  make format       - Format code"
	@echo "  make typecheck    - Run type checker"
	@echo "  make clean        - Clean build artifacts"
	@echo "  make run          - Run CLI (use ARGS='...' for arguments)"

install:
	uv pip install -e .

install-dev:
	uv pip install -e ".[dev]"

test:
	uv run pytest

test-cov:
	uv run pytest --cov=pr_jira_tool --cov-report=html --cov-report=term

lint:
	uvx ruff check .

format:
	uvx ruff format .

typecheck:
	uvx mypy pr_jira_tool/

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

run:
	uv run pr-jira $(ARGS)

# Example: make run ARGS="review --pr owner/repo#123 --dry-run"
