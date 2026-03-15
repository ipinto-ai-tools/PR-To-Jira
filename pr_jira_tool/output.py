"""Output formatting for CLI results."""

from rich.console import Console
from rich.panel import Panel

from pr_jira_tool.models import OperationResult


class OutputFormatter:
    """Formats operation results for display."""

    def __init__(self, verbose: bool = False) -> None:
        """
        Initialize output formatter.

        Args:
            verbose: Enable verbose output.
        """
        self.verbose = verbose
        self.console = Console()

    def print_result(self, result: OperationResult) -> None:
        """
        Print operation result in human-readable format.

        Args:
            result: Operation result to display.
        """
        # Create title
        title = f"PR Summary for {result.pr_url}"

        # Build content
        lines = []
        lines.append(f"[bold]Title:[/bold] {result.title}")
        lines.append(f"[bold]Classification:[/bold] {result.classification}")

        if result.jira_ticket:
            lines.append(f"[bold]Jira Ticket:[/bold] {result.jira_ticket}")

        lines.append("")
        lines.append("[bold]Summary:[/bold]")
        lines.append(result.summary)

        # Add actions taken
        if result.dry_run:
            lines.append("")
            lines.append("[yellow]DRY RUN - No changes were made[/yellow]")

        lines.append("")
        lines.append("[bold]Actions:[/bold]")

        actions = []
        if result.linked_to_jira:
            actions.append("✓ Added remote link to Jira ticket")
        elif result.jira_ticket and not result.dry_run:
            actions.append("○ Link already exists on Jira ticket")

        if result.commented_on_pr:
            actions.append("✓ Posted summary comment to PR")
        elif not result.dry_run:
            actions.append("○ Comment already exists on PR")

        lines.extend(actions)

        # Add errors if any
        if result.errors:
            lines.append("")
            lines.append("[bold red]Errors:[/bold red]")
            for error in result.errors:
                lines.append(f"✗ {error}")

        # Create panel
        content = "\n".join(lines)
        panel = Panel(
            content,
            title=title,
            border_style="blue",
            padding=(1, 2),
        )

        self.console.print(panel)

    def print_info(self, message: str) -> None:
        """Print informational message."""
        if self.verbose:
            self.console.print(f"[blue]ℹ[/blue] {message}")

    def print_success(self, message: str) -> None:
        """Print success message."""
        self.console.print(f"[green]✓[/green] {message}")

    def print_warning(self, message: str) -> None:
        """Print warning message."""
        self.console.print(f"[yellow]⚠[/yellow] {message}")

    def print_error(self, message: str) -> None:
        """Print error message."""
        self.console.print(f"[red]✗[/red] {message}")
