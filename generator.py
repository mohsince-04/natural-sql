import os
import sys
from pathlib import Path
import typer
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from google import genai
from google.genai import types

from schemas import SQLGenerationResponse

app = typer.Typer(help="Natural Language to SQL Query Generator CLI")
console = Console()


def extract_text(file_path: str) -> str:
    path = Path(file_path)
    if not path.exists():
        console.print(f"[bold red]Error: File not found -> {file_path}[/bold red]")
        raise typer.Exit(1)

    try:
        return path.read_text(encoding="utf-8")
    except Exception as e:
        console.print(f"[bold red]Failed to read file: {e}[/bold red]")
        raise typer.Exit(1)


@app.command()
def generate(
    question: str = typer.Argument(
        ..., help="Natural language question or request for the database"
    ),
    schema: str = typer.Option(
        ...,
        "--schema",
        "-s",
        help="Path to database schema file (.sql) or inline schema string",
    ),
    dialect: str = typer.Option(
        "PostgreSQL",
        "--dialect",
        "-d",
        help="Target SQL dialect (PostgreSQL, MySQL, SQLite, etc.)",
    ),
):
    """Translate natural language into a formatted, syntax-checked SQL query against a target schema."""

    if not os.environ.get("GEMINI_API_KEY"):
        console.print(
            "[bold red]Error: GEMINI_API_KEY environment variable is not set.[/bold red]"
        )
        raise typer.Exit(1)

    # Handle schema being a file path or inline text
    if Path(schema).exists():
        schema_text = extract_text(schema)
    else:
        schema_text = schema

    client = genai.Client()

    prompt = f"""
You are an expert senior database administrator and SQL optimization engineer. 
Given the database schema below, translate the user's natural language request into a precise, highly optimized, and formatted {dialect} query.

=== DATABASE SCHEMA ===
{schema_text}

=== USER REQUEST ===
{question}
"""

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(
            description=f"Generating {dialect} query with Gemini...", total=None
        )

        try:
            # Temporarily suppress stderr to keep terminal output clean
            original_stderr = sys.stderr
            sys.stderr = open(os.devnull, "w")
            try:
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=SQLGenerationResponse,
                        temperature=0.1,
                    ),
                )
            finally:
                sys.stderr.close()
                sys.stderr = original_stderr

            result = SQLGenerationResponse.model_validate_json(response.text)
        except Exception as e:
            console.print(f"[bold red]SQL Generation failed: {e}[/bold red]")
            raise typer.Exit(1)

    # Render Dashboard using Rich
    console.print("\n")
    console.print(
        Panel.fit(
            f"[bold cyan]⚡ SQL Query Generator Report[/bold cyan]\n"
            f"Target Dialect: [bold green]{result.dialect}[/bold green]",
            title="Natural Language to SQL",
            border_style="cyan",
        )
    )

    # Render SQL Code Block with Rich Syntax Highlighting
    sql_syntax = Syntax(result.sql_query, "sql", theme="monokai", line_numbers=True)
    console.print(
        Panel(
            sql_syntax,
            title="[bold yellow]💻 Generated SQL Query[/bold yellow]",
            border_style="yellow",
        )
    )

    # Metadata Table
    meta_table = Table(show_header=True, header_style="bold magenta")
    meta_table.add_column("Metadata Property", style="dim")
    meta_table.add_column("Details", justify="right")

    meta_table.add_row(
        "Tables Involved",
        ", ".join([f"[bold blue]{t}[/bold blue]" for t in result.tables_involved]),
    )
    console.print(meta_table)

    # Explanation Panel
    console.print(
        Panel(
            result.explanation,
            title="[bold blue]📖 Query Explanation[/bold blue]",
            border_style="blue",
        )
    )

    # Edge Cases Panel
    edges_text = "\n".join([f"• {edge}" for edge in result.potential_edge_cases])
    console.print(
        Panel(
            edges_text,
            title="[bold red]⚠️ Performance & Edge Cases[/bold red]",
            border_style="red",
        )
    )
    console.print("\n")


if __name__ == "__main__":
    app()
