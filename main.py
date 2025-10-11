import typer
import sys
import os
from rich.console import Console
from rich.table import Table

from mongodb import fetch_team_members

# Add the src directory to the path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.commands.test_connection import test_connection_command
from src.commands.prompt import prompt_command

app = typer.Typer(
    name="speckit",
    help="A CLI tool for managing specifications with VoyageAI embeddings and MongoDB vector search."
)


@app.command()
def hello(name: str):
    """Say hello to someone."""
    print(f"Hello {name}")


@app.command()
def goodbye(name: str):
    """Say goodbye to someone."""
    print(f"Goodbye {name}")


@app.command("test-connection")
def test_connection(
    service: str = typer.Option(None, "--service", "-s", help="Test specific service: 'voyageai' or 'mongodb'"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed output"),
    api_key: str = typer.Option(None, "--api-key", help="VoyageAI API key for testing")
):
    """Test connections to VoyageAI and MongoDB services."""
    test_connection_command(service, verbose, api_key)


@app.command("prompt")
def prompt(
    text: str = typer.Argument(..., help="The text prompt to process with VoyageAI"),
    model: str = typer.Option(None, "--model", "-m", help="VoyageAI model to use (default: voyage-code-2)"),
    api_key: str = typer.Option(None, "--api-key", help="VoyageAI API key"),
    output_format: str = typer.Option("summary", "--format", "-f", help="Output format: summary, full, json, embedding"),
    input_type: str = typer.Option("document", "--input-type", help="Input type: document, query"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed output")
):
    """Process text with VoyageAI and return embeddings or analysis."""
    prompt_command(text, model, api_key, output_format, input_type, verbose)
@app.command()
def team():
    console = Console()
    team_members = fetch_team_members()

    if not team_members:
        console.print("[red]No team members found.[/red]")
        return

    # Create a beautiful table
    table = Table(title="🚀 Vibe Engineering Team", title_style="bold magenta")
    table.add_column("#", style="cyan", justify="center", width=4)
    table.add_column("Name", style="green", justify="left")
    table.add_column("Status", style="bright_blue", justify="center")

    # Add team members to the table
    for i, member in enumerate(team_members, 1):
        table.add_row(str(i), member, "✨ Active")

    # Display the table with some extra styling
    console.print()
    console.print(table)
    console.print(
        f"\n[bold blue]Total Team Members:[/bold blue] [yellow]{len(team_members)}[/yellow]"
    )


if __name__ == "__main__":
    app()
