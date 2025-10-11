"""CLI commands for vibe-engineering."""
import typer
from rich.console import Console
from rich.table import Table

from src.db import MongoDBClient, TeamRepository
from src.llm import FireworksClient
from src.schemas import SpecifySchema

app = typer.Typer()


@app.command()
def hello(name: str):
    """Say hello to someone."""
    print(f"Hello {name}")


@app.command()
def goodbye(name: str):
    """Say goodbye to someone."""
    print(f"Goodbye {name}")


@app.command()
def team():
    """Display the team members from the database."""
    console = Console()

    with MongoDBClient() as db_client:
        team_repo = TeamRepository(db_client)
        team_members = team_repo.fetch_all_members()

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


@app.command()
def specify(prompt: str):
    """Generate a specification schema using LLM."""
    try:
        llm_client = FireworksClient()
        response = llm_client.generate_with_schema(
            prompt=prompt,
            schema=SpecifySchema.model_json_schema(),
            schema_name="SpecifySchema",
        )

        console = Console()
        console.print(response)
    except Exception as e:
        console = Console()
        console.print(f"[red]Error:[/red] {e}")


if __name__ == "__main__":
    app()
