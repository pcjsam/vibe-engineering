"""CLI commands for vibe-engineering."""

import json
import uuid
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from src.db import MongoDBClient, get_documents, insert_document
from src.llm import FireworksClient
from src.schemas import Plan, Requirement

app = typer.Typer()

# Path to the session ID file
SESSION_ID_FILE = Path(".session_id.txt")


def get_session_id() -> Optional[str]:
    """Read the session ID from the file. Returns None if file doesn't exist or is empty."""
    try:
        if SESSION_ID_FILE.exists():
            session_id = SESSION_ID_FILE.read_text().strip()
            return session_id if session_id else None
        return None
    except Exception:
        return None


@app.command()
def init():
    """Initialize a new session by generating a random ID and storing it in .session_id.txt."""
    console = Console()

    try:
        # Generate a random UUID
        session_id = str(uuid.uuid4())

        # Write to file
        SESSION_ID_FILE.write_text(session_id)

        console.print("[green]✓[/green] Session initialized successfully!")
        console.print(f"[dim]Session ID: {session_id}[/dim]")
        console.print(f"[dim]Stored in: {SESSION_ID_FILE.absolute()}[/dim]")

    except Exception as e:
        console.print(f"[red]Error initializing session:[/red] {e}")
        raise typer.Exit(1)


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
                db_client=db_client, db_name="master", collection_name="team", query={}
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
def requirements(prompt: str, db_name: str = "master", collection_name: str = "llm"):
    """Generate a requirement schema using LLM and store it in MongoDB."""
    console = Console()

    try:
        # Check for session ID
        session_id = get_session_id()
        if session_id is None:
            console.print(
                "[red]Error:[/red] No session initialized. Please run 'init' command first."
            )
            raise typer.Exit(1)

        console.print(f"[dim]Using session ID: {session_id}[/dim]\n")

        # Generate schema using LLM with session_id context
        llm_client = FireworksClient()
        prompt_with_session = f"Session ID: {session_id}\n\n{prompt}"
        response = llm_client.generate_with_schema(
            prompt=prompt_with_session,
            schema=Requirement.model_json_schema(),
            schema_name="Requirement",
        )

        # Parse the JSON response
        doc = json.loads(response)

        # Store in MongoDB
        with MongoDBClient() as db_client:
            inserted_id = insert_document(
                db_client=db_client,
                db_name=db_name,
                collection_name=collection_name,
                document=doc,
            )

        console.print(
            f"[green]✓[/green] Document stored in {db_name}.{collection_name}"
        )
        console.print(f"[dim]Document ID: {inserted_id}[/dim]\n")

        # Create a copy of doc for display, converting ObjectId to string if present
        display_doc = doc.copy()
        if "_id" in display_doc:
            display_doc["_id"] = str(display_doc["_id"])

        # Pretty print the schema with rich
        console.print("[bold cyan]Generated Requirement:[/bold cyan]")
        from rich.syntax import Syntax

        json_str = json.dumps(display_doc, indent=2, default=str)
        syntax = Syntax(json_str, "json", theme="monokai", line_numbers=False)
        console.print(syntax)

    except json.JSONDecodeError as e:
        console.print(f"[red]Error parsing JSON response:[/red] {e}")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")


@app.command()
def plan(prompt: Optional[str] = typer.Argument(None)):
    """Generate a plan using LLM based on requirements and store it in MongoDB."""
    console = Console()
    db_name = "master"
    collection_name = "llm"

    try:
        # Check for session ID
        session_id = get_session_id()
        if session_id is None:
            console.print(
                "[red]Error:[/red] No session initialized. Please run 'init' command first."
            )
            raise typer.Exit(1)

        console.print(f"[dim]Using session ID: {session_id}[/dim]\n")

        # Fetch all Requirements documents for this session
        with MongoDBClient() as db_client:
            requirements_docs = get_documents(
                db_client=db_client,
                db_name=db_name,
                collection_name=collection_name,
                query={"type": "Requirement", "session_id": session_id},
            )

        # Format requirements for the prompt
        requirements_text = ""
        if requirements_docs:
            console.print(f"[dim]Found {len(requirements_docs)} requirement(s)[/dim]\n")
            requirements_text = "\n\n# Requirements:\n"
            for idx, req in enumerate(requirements_docs, 1):
                requirements_text += f"\n## Requirement {idx}:\n"
                requirements_text += f"- Priority: {req.get('priority', 'N/A')}\n"
                requirements_text += f"- Component: {req.get('component', 'N/A')}\n"
                requirements_text += f"- User Story: {req.get('user_story', 'N/A')}\n"
                requirements_text += f"- Acceptance: {req.get('acceptance', 'N/A')}\n"
        else:
            console.print("[yellow]No requirements found for this session[/yellow]\n")

        # Use default prompt if empty
        if not prompt or not prompt.strip():
            prompt = """
Frontend: React + TypeScript + shadcn/ui + Tailwind + Vite;
Backend: Python FastAPI + Pymongo (MongoDB Atlas);
Embeddings: Voyage AI;
Testing: Vitest / Pytest;
Linting: ESLint + Ruff + Black
"""
            console.print("[dim]Using default tech stack prompt[/dim]\n")

        # Generate schema using LLM with session_id context
        llm_client = FireworksClient()
        full_prompt = f"Session ID: {session_id}\n\n{prompt}{requirements_text}"
        system_prompt = """
            You are a senior architect planning a web application.
            Create three planning notes: ADR, design-high, and design-low.
            Each must include a session_id to link back to this run.
        """
        response = llm_client.generate_with_schema(
            prompt=full_prompt,
            schema=Plan.model_json_schema(),
            schema_name="Plan",
            system_prompt=system_prompt,
        )

        # Parse the JSON response
        doc = json.loads(response)

        # Store in MongoDB
        with MongoDBClient() as db_client:
            inserted_id = insert_document(
                db_client=db_client,
                db_name=db_name,
                collection_name=collection_name,
                document=doc,
            )

        console.print(
            f"[green]✓[/green] Document stored in {db_name}.{collection_name}"
        )
        console.print(f"[dim]Document ID: {inserted_id}[/dim]\n")

        # Create a copy of doc for display, converting ObjectId to string if present
        display_doc = doc.copy()
        if "_id" in display_doc:
            display_doc["_id"] = str(display_doc["_id"])

        # Pretty print the schema with rich
        console.print("[bold cyan]Generated Requirement:[/bold cyan]")
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
