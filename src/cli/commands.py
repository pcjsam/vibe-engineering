"""CLI commands for vibe-engineering."""
import json

import typer
from rich.console import Console
from rich.table import Table

from src.db import MongoDBClient, get_documents, insert_document
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

    try:
        with MongoDBClient() as db_client:
            documents = get_documents(
                db_client=db_client,
                db_name="master",
                collection_name="team",
                query={}
            )
            team_members = [doc["name"] for doc in documents]

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
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")


@app.command()
def specify(prompt: str, db_name: str = "master", collection_name: str = "llm"):
    """Generate a specification schema using LLM and store it in MongoDB."""
    console = Console()

    try:
        # Generate schema using LLM
        llm_client = FireworksClient()
        response = llm_client.generate_with_schema(
            prompt=prompt,
            schema=SpecifySchema.model_json_schema(),
            schema_name="SpecifySchema",
        )

        # Parse the JSON response
        doc = json.loads(response)

        # Store in MongoDB
        with MongoDBClient() as db_client:
            inserted_id = insert_document(
                db_client=db_client,
                db_name=db_name,
                collection_name=collection_name,
                document=doc
            )

        console.print(f"[green]✓[/green] Document stored in {db_name}.{collection_name}")
        console.print(f"[dim]Document ID: {inserted_id}[/dim]\n")

        # Create a copy of doc for display, converting ObjectId to string if present
        display_doc = doc.copy()
        if "_id" in display_doc:
            display_doc["_id"] = str(display_doc["_id"])

        # Pretty print the schema with rich
        console.print("[bold cyan]Generated Schema:[/bold cyan]")
        from rich.syntax import Syntax
        json_str = json.dumps(display_doc, indent=2, default=str)
        syntax = Syntax(json_str, "json", theme="monokai", line_numbers=False)
        console.print(syntax)

    except json.JSONDecodeError as e:
        console.print(f"[red]Error parsing JSON response:[/red] {e}")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")


if __name__ == "__main__":
    app()
