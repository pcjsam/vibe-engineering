import typer
from rich.console import Console
from rich.table import Table

from llm import get_llm_response
from mongodb import fetch_team_members

app = typer.Typer()


@app.command()
def hello(name: str):
    print(f"Hello {name}")


@app.command()
def goodbye(name: str):
    print(f"Goodbye {name}")


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


@app.command()
def llm():
    response = get_llm_response()
    console = Console()
    console.print(response)


if __name__ == "__main__":
    app()
