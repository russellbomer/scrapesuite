"""Interactive blueprint builder."""

import json
from pathlib import Path
from typing import Any


from scrapesuite.lib.http import get_html
from scrapesuite.lib.schemas import ExtractionSchema, FieldSchema, PaginationSchema


def build_schema_interactive(
    url: str | None = None,
    analysis: dict[str, Any] | None = None,
    html: str | None = None
) -> ExtractionSchema:
    """
    Build extraction schema interactively.
    
    Args:
        url: Optional URL to analyze
        analysis: Optional pre-computed analysis from Probe
        html: Optional HTML content
    
    Returns:
        Complete ExtractionSchema
    """
    try:
        from rich.console import Console
        from rich.prompt import Prompt, Confirm
        from rich.panel import Panel
        from rich.table import Table
        
        console = Console()
        console.print("\n[bold cyan]🔨 Blueprint Builder[/bold cyan]")
        console.print("[dim]Create an extraction schema interactively[/dim]\n")
    except ImportError:
        # Fallback without rich
        return _build_schema_simple(url, analysis, html)
    
    # Step 1: Schema metadata
    console.print(Panel("[bold]Step 1: Schema Metadata[/bold]", border_style="cyan"))
    
    name = Prompt.ask("Schema name", default="extraction")
    description = Prompt.ask("Description (optional)", default="")
    
    # Step 2: Get URL if not provided
    if not url and not html:
        url = Prompt.ask("Target URL (or leave empty for generic schema)", default="")
        if url and url.strip():
            console.print(f"[dim]Fetching {url}...[/dim]")
            try:
                html = get_html(url)
            except Exception as e:
                console.print(f"[red]Error fetching URL: {e}[/red]")
                html = None
    
    # Step 3: Item selector
    console.print(Panel("\n[bold]Step 2: Item Selector[/bold]", border_style="cyan"))
    console.print("This selector identifies each item to extract (e.g., article, product, post)\n")
    
    if analysis and analysis.get("containers"):
        # Show suggestions from Probe analysis
        containers = analysis["containers"][:5]
        
        table = Table(title="Suggested Containers", show_header=True)
        table.add_column("Option", style="cyan", width=8)
        table.add_column("Selector", style="yellow")
        table.add_column("Items", style="green", justify="right")
        
        for idx, container in enumerate(containers, 1):
            selector = container.get("child_selector", container.get("selector"))
            count = container.get("item_count", 0)
            table.add_row(str(idx), selector, str(count))
        
        console.print(table)
        
        choice = Prompt.ask(
            "\nSelect option or enter custom selector",
            default="1"
        )
        
        if choice.isdigit() and 1 <= int(choice) <= len(containers):
            item_selector = containers[int(choice) - 1].get("child_selector")
        else:
            item_selector = choice
    else:
        item_selector = Prompt.ask("Item selector (CSS)", default=".item")
    
    # Step 4: Fields
    console.print(Panel("\n[bold]Step 3: Fields[/bold]", border_style="cyan"))
    console.print("Define fields to extract from each item\n")
    
    fields = {}
    
    # Suggest fields from Probe if available
    suggested_fields = []
    if analysis and analysis.get("suggestions", {}).get("field_candidates"):
        suggested_fields = analysis["suggestions"]["field_candidates"][:5]
    
    if suggested_fields:
        console.print("[dim]Suggested fields from analysis:[/dim]")
        for idx, field in enumerate(suggested_fields, 1):
            console.print(f"  {idx}. {field['name']}: {field['selector']}")
        console.print()
        
        if Confirm.ask("Use suggested fields?", default=True):
            for field in suggested_fields:
                fields[field["name"]] = FieldSchema(selector=field["selector"])
    
    # Manual field entry
    while True:
        if fields:
            if not Confirm.ask("\nAdd another field?", default=True):
                break
        else:
            console.print("[yellow]No fields defined yet. Add at least one field.[/yellow]")
        
        field_name = Prompt.ask("Field name")
        selector = Prompt.ask(f"Selector for '{field_name}'")
        
        # Ask for attribute if it looks like a link/image
        attribute = None
        if "href" in selector.lower() or field_name.lower() in ["url", "link"]:
            attribute = Prompt.ask("Extract attribute", default="href")
        elif "src" in selector.lower() or field_name.lower() in ["image", "img"]:
            attribute = Prompt.ask("Extract attribute", default="src")
        
        required = Confirm.ask(f"Is '{field_name}' required?", default=False)
        
        fields[field_name] = FieldSchema(
            selector=selector,
            attribute=attribute if attribute else None,
            required=required
        )
        
        console.print(f"[green]✓[/green] Added field: {field_name}")
    
    # Step 5: Pagination (optional)
    console.print(Panel("\n[bold]Step 4: Pagination (Optional)[/bold]", border_style="cyan"))
    
    pagination = None
    if Confirm.ask("Does this page have pagination?", default=False):
        next_selector = Prompt.ask("Next page link selector", default="a.next")
        max_pages = Prompt.ask("Max pages to scrape (optional)", default="")
        
        pagination = PaginationSchema(
            next_selector=next_selector,
            max_pages=int(max_pages) if max_pages.strip() else None
        )
    
    # Build schema
    schema = ExtractionSchema(
        name=name,
        description=description if description.strip() else None,
        url=url if url and url.strip() else None,
        item_selector=item_selector,
        fields=fields,
        pagination=pagination
    )
    
    # Summary
    console.print(Panel("\n[bold green]✓ Schema Created[/bold green]", border_style="green"))
    console.print(f"Name: {schema.name}")
    console.print(f"Item selector: {schema.item_selector}")
    console.print(f"Fields: {len(schema.fields)}")
    if schema.pagination:
        console.print(f"Pagination: enabled")
    
    return schema


def _build_schema_simple(
    url: str | None = None,
    analysis: dict[str, Any] | None = None,
    html: str | None = None
) -> ExtractionSchema:
    """Fallback builder without rich library."""
    print("\n=== Blueprint Builder ===\n")
    
    # Schema metadata
    name = input("Schema name [extraction]: ").strip() or "extraction"
    description = input("Description (optional): ").strip()
    
    # Item selector
    print("\nItem Selector:")
    if analysis and analysis.get("containers"):
        print("Suggested containers:")
        containers = analysis["containers"][:3]
        for idx, cont in enumerate(containers, 1):
            selector = cont.get("child_selector", cont.get("selector"))
            count = cont.get("item_count", 0)
            print(f"  {idx}. {selector} ({count} items)")
        
        choice = input("\nSelect option or enter custom [1]: ").strip() or "1"
        if choice.isdigit() and 1 <= int(choice) <= len(containers):
            item_selector = containers[int(choice) - 1].get("child_selector")
        else:
            item_selector = choice
    else:
        item_selector = input("Item selector: ").strip()
    
    # Fields
    print("\nFields:")
    fields = {}
    
    while True:
        if fields:
            add_more = input("\nAdd another field? [y/N]: ").strip().lower()
            if add_more not in ["y", "yes"]:
                break
        
        field_name = input("Field name: ").strip()
        if not field_name:
            break
        
        selector = input(f"Selector for '{field_name}': ").strip()
        fields[field_name] = FieldSchema(selector=selector)
    
    if not fields:
        raise ValueError("At least one field is required")
    
    # Build schema
    schema = ExtractionSchema(
        name=name,
        description=description if description else None,
        url=url if url else None,
        item_selector=item_selector,
        fields=fields
    )
    
    print(f"\n✓ Schema created: {name}")
    return schema


def load_analysis_from_file(path: str | Path) -> dict[str, Any]:
    """Load Probe analysis from JSON file."""
    path = Path(path)
    
    if not path.exists():
        raise FileNotFoundError(f"Analysis file not found: {path}")
    
    with path.open() as f:
        return json.load(f)
