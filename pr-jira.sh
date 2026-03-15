#!/bin/bash
set -euo pipefail

# PR-to-Jira Tool Wrapper Script
# Usage: ./pr-jira.sh [command] [options]

# Check if .env file exists
if [[ ! -f .env ]]; then
    echo "Error: .env file not found in the current directory."
    echo ""
    echo "Please create a .env file with the following variables:"
    echo "  JIRA_URL=https://your-jira-instance.atlassian.net"
    echo "  JIRA_EMAIL=your-email@example.com"
    echo "  JIRA_API_TOKEN=your-api-token"
    echo "  GITHUB_TOKEN=your-github-token"
    echo ""
    echo "See .env.example for a template."
    exit 1
fi

# Load environment variables from .env
echo "Loading environment variables from .env..."
set -a
source .env
set +a

# Run the tool using uv, passing all arguments
echo "Running pr-jira with uv..."
uv run pr-jira "$@"
