import typer
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
import sys
import os

# Add the src directory to the path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from voyageai_client import VoyageAIClient
from mongodb_client import MongoDBClient
from config import config

console = Console()


def test_connection_command(
    service: Optional[str] = typer.Option(None, "--service", "-s", help="Test specific service: 'voyageai' or 'mongodb'"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed output"),
    api_key: Optional[str] = typer.Option(None, "--api-key", help="VoyageAI API key for testing")
):
    """Test connections to VoyageAI and MongoDB services."""
    
    console.print("\n[bold blue]🔧 Testing Service Connections[/bold blue]\n")
    
    # Validate configuration first
    if verbose:
        validation = config.validate_config()
        if validation["issues"]:
            console.print("[bold red]Configuration Issues:[/bold red]")
            for issue in validation["issues"]:
                console.print(f"  ❌ {issue}")
        if validation["warnings"]:
            console.print("[bold yellow]Configuration Warnings:[/bold yellow]")
            for warning in validation["warnings"]:
                console.print(f"  ⚠️  {warning}")
        console.print()
    
    services_to_test = []
    if service == "voyageai":
        services_to_test = ["voyageai"]
    elif service == "mongodb":
        services_to_test = ["mongodb"]
    else:
        services_to_test = ["voyageai", "mongodb"]
    
    results = {}
    
    # Test VoyageAI
    if "voyageai" in services_to_test:
        console.print("[bold cyan]Testing VoyageAI Connection...[/bold cyan]")
        results["voyageai"] = test_voyageai(api_key, verbose)
        console.print()
    
    # Test MongoDB
    if "mongodb" in services_to_test:
        console.print("[bold cyan]Testing MongoDB Connection...[/bold cyan]")
        results["mongodb"] = test_mongodb(verbose)
        console.print()
    
    # Display summary
    display_summary(results, verbose)
    
    # Exit with error code if any service failed
    if any(not result["success"] for result in results.values()):
        raise typer.Exit(1)


def test_voyageai(api_key: Optional[str], verbose: bool) -> dict:
    try:
        # Use provided API key or get from config
        if api_key:
            client = VoyageAIClient(api_key=api_key)
        else:
            voyage_config = config.get_voyageai_config()
            client = VoyageAIClient(
                api_key=voyage_config.get("api_key"),
                model=voyage_config.get("model", "voyage-code-2")
            )
        
        result = client.test_connection()
        
        if result["success"]:
            console.print(f"  ✅ VoyageAI connection successful")
            if verbose:
                console.print(f"     Model: {result['model']}")
                console.print(f"     Latency: {result['latency_ms']}ms")
                console.print(f"     Embedding dimensions: {result['embedding_dimensions']}")
                if result.get("total_tokens"):
                    console.print(f"     Total tokens: {result['total_tokens']}")
        else:
            console.print(f"  ❌ VoyageAI connection failed")
            console.print(f"     Error: {result['error']}")
        
        return result
        
    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
            "message": f"VoyageAI test failed: {str(e)}"
        }
        console.print(f"  ❌ VoyageAI connection failed")
        console.print(f"     Error: {str(e)}")
        return error_result


def test_mongodb(verbose: bool) -> dict:
    try:
        mongodb_config = config.get_mongodb_config()
        client = MongoDBClient(
            uri=mongodb_config.get("uri"),
            database=mongodb_config.get("database", "speckit"),
            collection=mongodb_config.get("collection", "specifications"),
            vector_index=mongodb_config.get("vector_index", "spec_vector_index")
        )
        
        result = client.test_connection()
        
        if result["success"]:
            console.print(f"  ✅ MongoDB connection successful")
            if verbose:
                console.print(f"     Database: {result['database']}")
                console.print(f"     Collection: {result['collection']}")
                console.print(f"     Latency: {result['latency_ms']}ms")
                console.print(f"     MongoDB version: {result['mongodb_version']}")
                console.print(f"     Document count: {result['document_count']}")
                console.print(f"     Vector index exists: {'Yes' if result['vector_index_exists'] else 'No'}")
                if not result['vector_index_exists']:
                    console.print(f"     ⚠️  Vector index '{result['vector_index_name']}' not found")
        else:
            console.print(f"  ❌ MongoDB connection failed")
            console.print(f"     Error: {result['error']}")
        
        # Clean up
        client.close()
        return result
        
    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
            "message": f"MongoDB test failed: {str(e)}"
        }
        console.print(f"  ❌ MongoDB connection failed")
        console.print(f"     Error: {str(e)}")
        return error_result


def display_summary(results: dict, verbose: bool):
    """Display a summary table of test results."""
    
    table = Table(title="Connection Test Summary", show_header=True, header_style="bold magenta")
    table.add_column("Service", style="cyan", no_wrap=True)
    table.add_column("Status", justify="center")
    table.add_column("Latency", justify="right")
    table.add_column("Details")
    
    for service_name, result in results.items():
        status = "✅ Success" if result["success"] else "❌ Failed"
        latency = f"{result.get('latency_ms', 0):.1f}ms" if result.get('latency_ms') else "N/A"
        
        if result["success"]:
            if service_name == "voyageai":
                details = f"Model: {result.get('model', 'Unknown')}, Dims: {result.get('embedding_dimensions', 0)}"
            elif service_name == "mongodb":
                details = f"DB: {result.get('database', 'Unknown')}, Docs: {result.get('document_count', 0)}"
            else:
                details = result.get("message", "")
        else:
            details = result.get("error", "Unknown error")[:50] + ("..." if len(result.get("error", "")) > 50 else "")
        
        table.add_row(
            service_name.title(),
            status,
            latency,
            details
        )
    
    console.print(table)
    
    # Overall status
    all_success = all(result["success"] for result in results.values())
    if all_success:
        console.print("\n[bold green]🎉 All services are connected and working properly![/bold green]")
    else:
        failed_services = [name for name, result in results.items() if not result["success"]]
        console.print(f"\n[bold red]❌ Failed services: {', '.join(failed_services)}[/bold red]")
        console.print("\n[bold yellow]💡 Troubleshooting tips:[/bold yellow]")
        console.print("  • Check your API keys and connection strings")
        console.print("  • Ensure services are running and accessible")
        console.print("  • Verify your .env file or environment variables")
        console.print("  • Run with --verbose for more detailed information")


if __name__ == "__main__":
    typer.run(test_connection_command)