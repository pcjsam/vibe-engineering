import typer
import json
import sys
import os
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

# Add the src directory to the path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from voyageai_client import VoyageAIClient
from config import config

console = Console()


def prompt_command(
    text: str = typer.Argument(..., help="The text prompt to process with VoyageAI"),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="VoyageAI model to use (default: voyage-code-2)"),
    api_key: Optional[str] = typer.Option(None, "--api-key", help="VoyageAI API key"),
    output_format: str = typer.Option("summary", "--format", "-f", help="Output format: summary, full, json, embedding"),
    input_type: str = typer.Option("document", "--input-type", help="Input type: document, query"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed output")
):
    """Process text with VoyageAI and return embeddings or analysis."""
    
    if verbose:
        console.print(f"[cyan]Processing prompt with VoyageAI...[/cyan]")
        console.print(f"Text length: {len(text)} characters")
    
    try:
        # Initialize VoyageAI client
        voyage_config = config.get_voyageai_config()
        client_model = model or voyage_config.get("model", "voyage-code-2")
        client_api_key = api_key or voyage_config.get("api_key")
        
        if not client_api_key:
            console.print("[red]❌ Error: VoyageAI API key not found. Set VOYAGE_API_KEY environment variable or use --api-key option.[/red]")
            raise typer.Exit(1)
        
        client = VoyageAIClient(api_key=client_api_key, model=client_model)
        
        if verbose:
            console.print(f"Using model: {client_model}")
            console.print(f"Input type: {input_type}")
        
        # Generate embedding
        result = client.embed([text], input_type=input_type)
        embedding = result.embeddings[0]
        
        # Display results based on format
        if output_format == "embedding":
            display_embedding_only(embedding, verbose)
        elif output_format == "json":
            display_json_output(text, embedding, result, client_model, input_type)
        elif output_format == "full":
            display_full_output(text, embedding, result, client_model, input_type, verbose)
        else:  # summary (default)
            display_summary_output(text, embedding, result, client_model, verbose)
        
    except Exception as e:
        console.print(f"[red]❌ Error processing prompt: {str(e)}[/red]")
        if verbose:
            console.print(f"[red]Full error: {repr(e)}[/red]")
        raise typer.Exit(1)


def display_embedding_only(embedding, verbose):
    """Display only the embedding vector."""
    if verbose:
        console.print(f"Embedding dimensions: {len(embedding)}")
    
    # Print as JSON array for easy consumption
    print(json.dumps(embedding))


def display_json_output(text, embedding, result, model, input_type):
    """Display full output as JSON."""
    output = {
        "text": text,
        "model": model,
        "input_type": input_type,
        "embedding": embedding,
        "dimensions": len(embedding),
        "total_tokens": getattr(result, 'total_tokens', None)
    }
    print(json.dumps(output, indent=2))


def display_full_output(text, embedding, result, model, input_type, verbose):
    """Display comprehensive output with rich formatting."""
    console.print("\n[bold blue]🚀 VoyageAI Processing Results[/bold blue]\n")
    
    # Input information
    input_panel = Panel(
        f"[cyan]Text:[/cyan] {text[:200]}{'...' if len(text) > 200 else ''}\n"
        f"[cyan]Length:[/cyan] {len(text)} characters\n"
        f"[cyan]Model:[/cyan] {model}\n"
        f"[cyan]Input Type:[/cyan] {input_type}",
        title="Input Information",
        border_style="blue"
    )
    console.print(input_panel)
    
    # Embedding information
    embedding_info = (
        f"[green]Dimensions:[/green] {len(embedding)}\n"
        f"[green]Sample values:[/green] [{embedding[0]:.6f}, {embedding[1]:.6f}, {embedding[2]:.6f}, ...]\n"
    )
    
    if hasattr(result, 'total_tokens') and result.total_tokens:
        embedding_info += f"[green]Total tokens:[/green] {result.total_tokens}\n"
    
    embedding_panel = Panel(
        embedding_info,
        title="Embedding Information",
        border_style="green"
    )
    console.print(embedding_panel)
    
    if verbose:
        # Show first 10 embedding values
        sample_embedding = embedding[:10]
        console.print("\n[yellow]First 10 embedding values:[/yellow]")
        for i, val in enumerate(sample_embedding):
            console.print(f"  [{i}]: {val:.8f}")


def display_summary_output(text, embedding, result, model, verbose):
    """Display a concise summary of the results."""
    console.print(f"\n[green]✅ Successfully processed text with {model}[/green]")
    console.print(f"[cyan]Text length:[/cyan] {len(text)} characters")
    console.print(f"[cyan]Embedding dimensions:[/cyan] {len(embedding)}")
    
    if hasattr(result, 'total_tokens') and result.total_tokens:
        console.print(f"[cyan]Tokens used:[/cyan] {result.total_tokens}")
    
    # Show embedding summary
    console.print(f"[cyan]Embedding range:[/cyan] [{min(embedding):.4f}, {max(embedding):.4f}]")
    
    if verbose:
        console.print(f"\n[yellow]Sample embedding values:[/yellow]")
        console.print(f"[{embedding[0]:.6f}, {embedding[1]:.6f}, {embedding[2]:.6f}, ...]")


if __name__ == "__main__":
    typer.run(prompt_command)