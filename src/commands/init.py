import typer
import asyncio
import os
import sys
from typing import Optional, List
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from services.memory_service import MemoryService
from models import DEFAULT_PRINCIPLES, DEFAULT_GUIDELINES, Project
from config import config

console = Console()


def init_command(
    slug: str = typer.Argument(..., help="Project slug (unique identifier)"),
    repo_url: str = typer.Argument(..., help="Repository URL"),
    owners: Optional[List[str]] = typer.Option(None, "--owner", "-o", help="Project owners (can specify multiple times)"),
    skip_defaults: bool = typer.Option(False, "--skip-defaults", help="Skip seeding with default principles and guidelines"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed output")
):
    """Initialize a new project with principles and guidelines."""
    
    # Run the async function
    asyncio.run(init_project_async(slug, repo_url, owners or [], skip_defaults, verbose))


async def init_project_async(slug: str, repo_url: str, owners: List[str], skip_defaults: bool, verbose: bool):
    """Async implementation of project initialization."""
    
    console.print(f"\n[bold blue]🚀 Initializing project '{slug}'[/bold blue]\n")
    
    # Validate configuration
    if verbose:
        validation = config.validate_config()
        if validation["issues"]:
            console.print("[red]❌ Configuration issues found:[/red]")
            for issue in validation["issues"]:
                console.print(f"  • {issue}")
            console.print("\n[yellow]Please fix configuration issues before proceeding.[/yellow]")
            raise typer.Exit(1)
    
    memory_service = None
    try:
        # Initialize memory service
        memory_service = MemoryService()
        
        # Check if project already exists
        existing_project = memory_service.get_project_by_slug(slug)
        if existing_project:
            console.print(f"[red]❌ Project '{slug}' already exists![/red]")
            console.print(f"Created: {existing_project.created_at}")
            console.print(f"Repository: {existing_project.repo_url}")
            raise typer.Exit(1)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            
            # Create project
            task1 = progress.add_task("Creating project...", total=None)
            project = await memory_service.create_project(
                slug=slug,
                repo_url=repo_url,
                owners=owners
            )
            progress.update(task1, completed=True)
            
            # Seed with principles and guidelines
            if not skip_defaults:
                task2 = progress.add_task("Seeding principles and guidelines...", total=None)
                notes = await memory_service.seed_principles_and_guidelines(
                    project_id=project.id,
                    principles=DEFAULT_PRINCIPLES,
                    guidelines=DEFAULT_GUIDELINES
                )
                progress.update(task2, completed=True)
            else:
                notes = []
        
        # Display success message
        console.print("\n[green]✅ Project initialized successfully![/green]\n")
        
        # Show project details
        display_project_summary(project, notes, verbose)
        
        # Show next steps
        display_next_steps(slug)
        
    except Exception as e:
        console.print(f"[red]❌ Error initializing project: {str(e)}[/red]")
        if verbose:
            console.print(f"[red]Full error: {repr(e)}[/red]")
        raise typer.Exit(1)
    
    finally:
        if memory_service:
            memory_service.close()


def display_project_summary(project: Project, notes: List, verbose: bool):
    """Display a summary of the created project."""
    
    # Project info panel
    project_info = (
        f"[cyan]ID:[/cyan] {project.id}\n"
        f"[cyan]Slug:[/cyan] {project.slug}\n"
        f"[cyan]Repository:[/cyan] {project.repo_url}\n"
        f"[cyan]Created:[/cyan] {project.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"[cyan]Owners:[/cyan] {', '.join(project.owners) if project.owners else 'None'}"
    )
    
    project_panel = Panel(
        project_info,
        title="📋 Project Details",
        border_style="blue"
    )
    console.print(project_panel)
    
    # Notes summary
    if notes:
        console.print(f"\n[green]📝 Seeded {len(notes)} default notes:[/green]")
        
        if verbose:
            # Show detailed table
            table = Table(title="Seeded Notes", show_header=True, header_style="bold magenta")
            table.add_column("Type", style="cyan", no_wrap=True)
            table.add_column("Title", style="green")
            table.add_column("Tags", style="yellow")
            
            for note in notes:
                table.add_row(
                    note.type.title(),
                    note.title,
                    ", ".join(note.tags[:3]) + ("..." if len(note.tags) > 3 else "")
                )
            
            console.print(table)
        else:
            # Show summary counts
            principles_count = len([n for n in notes if n.type == "principle"])
            guidelines_count = len([n for n in notes if n.type == "guideline"])
            console.print(f"  • [cyan]{principles_count}[/cyan] principles")
            console.print(f"  • [cyan]{guidelines_count}[/cyan] guidelines")


def display_next_steps(slug: str):
    """Display suggested next steps."""
    
    next_steps = f"""[bold yellow]🎯 Next Steps:[/bold yellow]

1. **Create requirements:**
   [dim]python main.py specify "Add user authentication" --project {slug}[/dim]

2. **Plan the implementation:**
   [dim]python main.py plan --project {slug} --scope "authentication"[/dim]

3. **Break down into tasks:**
   [dim]python main.py tasks --project {slug}[/dim]

4. **Search project memory:**
   [dim]python main.py recall "security principles" --project {slug}[/dim]

5. **Render documentation:**
   [dim]python main.py render --project {slug} --output docs/[/dim]

[dim]💡 Use --help with any command for more options[/dim]"""
    
    console.print(Panel(next_steps, title="🚀 Get Started", border_style="yellow"))


if __name__ == "__main__":
    typer.run(init_command)