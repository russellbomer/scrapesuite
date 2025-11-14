"""Interactive field editor for survey builder."""

from collections import OrderedDict

from bs4 import BeautifulSoup
from rich.console import Console
from rich.prompt import Confirm, Prompt
from rich.table import Table

from quarry.lib.schemas import FieldSchema


console = Console()


def edit_fields_interactive(
    fields: dict[str, FieldSchema],
    html: str | None = None,
    item_selector: str | None = None
) -> dict[str, FieldSchema]:
    """
    Interactive field editor with add/remove/rename/reorder/preview.
    
    Args:
        fields: Initial fields dict
        html: Optional HTML for preview
        item_selector: Item container selector for preview
    
    Returns:
        Modified fields dict
    """
    # Convert to OrderedDict to maintain order
    fields = OrderedDict(fields)
    
    console.print("\n" + "═" * 60)
    console.print("[bold cyan]Field Configuration[/bold cyan]")
    console.print("═" * 60)
    console.print(
        "[dim]Commands: [/dim]"
        "[cyan]a[/cyan]dd | "
        "[yellow]r[/yellow]emove | "
        "[magenta]e[/magenta]dit | "
        "[blue]m[/blue]ove | "
        "[green]p[/green]review | "
        "[white]d[/white]one"
    )
    console.print()
    
    while True:
        # Show current fields
        _display_fields_table(fields)
        
        console.print()
        cmd = Prompt.ask(
            "What would you like to do?",
            choices=["add", "remove", "edit", "move", "preview", "done", "a", "r", "e", "m", "p", "d"],
            default="done"
        )
        
        # Normalize shortcuts
        cmd_map = {"a": "add", "r": "remove", "e": "edit", "m": "move", "p": "preview", "d": "done"}
        cmd = cmd_map.get(cmd, cmd)
        
        if cmd == "add":
            _add_field(fields, html, item_selector)
        elif cmd == "remove":
            _remove_field(fields)
        elif cmd == "edit":
            _edit_field(fields, html, item_selector)
        elif cmd == "move":
            _reorder_fields(fields)
        elif cmd == "preview":
            if html and item_selector:
                _preview_extraction(html, item_selector, fields)
            else:
                console.print("[yellow]⚠ No HTML available for preview[/yellow]")
        elif cmd == "done":
            break
        
        console.print()
    
    return dict(fields)


def _display_fields_table(fields: dict[str, FieldSchema]) -> None:
    """Display current fields in a table."""
    table = Table(title="Current Fields", show_header=True, header_style="bold cyan")
    table.add_column("#", style="dim", width=3)
    table.add_column("Field Name", style="cyan")
    table.add_column("Selector", style="green")
    table.add_column("Attribute", style="yellow")
    table.add_column("Required", style="magenta", width=8)
    
    for i, (name, field) in enumerate(fields.items(), 1):
        table.add_row(
            str(i),
            name,
            field.selector[:40] + "..." if len(field.selector) > 40 else field.selector,
            field.attribute or "—",
            "✓" if field.required else ""
        )
    
    if not fields:
        table.add_row("—", "[dim]No fields yet[/dim]", "", "", "")
    
    console.print(table)


def _add_field(
    fields: OrderedDict,
    html: str | None,
    item_selector: str | None
) -> None:
    """Add a new field with selector suggestions."""
    console.print("\n[bold]Add New Field[/bold]")
    
    # Show available selectors if HTML provided
    if html and item_selector:
        suggestions = _get_selector_suggestions(html, item_selector)
        if suggestions:
            console.print("\n[dim]Available selectors in items:[/dim]")
            for i, (sel, preview) in enumerate(suggestions[:15], 1):
                console.print(f"  {i:2}. [cyan]{sel:25}[/cyan] → [dim]{preview[:40]}[/dim]")
            console.print()
    
    # Get field name
    field_name = Prompt.ask("Field name").strip()
    if not field_name:
        console.print("[yellow]Cancelled[/yellow]")
        return
    
    if field_name in fields:
        if not Confirm.ask(f"Field '{field_name}' exists. Replace?", default=False):
            return
    
    # Get selector (allow number selection if suggestions shown)
    selector_prompt = "Selector (or number from above)" if html and item_selector else "Selector"
    selector = Prompt.ask(selector_prompt).strip()
    
    if not selector:
        console.print("[yellow]Cancelled[/yellow]")
        return
    
    # Check if number selection
    if selector.isdigit() and html and item_selector:
        suggestions = _get_selector_suggestions(html, item_selector)
        idx = int(selector) - 1
        if 0 <= idx < len(suggestions):
            selector = suggestions[idx][0]
            console.print(f"[green]✓[/green] Using: [cyan]{selector}[/cyan]")
    
    # Get optional attribute
    attribute = Prompt.ask("Attribute (optional, e.g., 'href', 'src')", default="").strip()
    
    # Get required flag
    required = Confirm.ask("Required field?", default=False)
    
    # Create field
    fields[field_name] = FieldSchema(
        selector=selector,
        attribute=attribute if attribute else None,
        required=required
    )
    
    # Preview extraction if HTML available
    if html and item_selector:
        console.print("\n[dim]Preview:[/dim]")
        _preview_single_field(html, item_selector, field_name, fields[field_name])
    
    console.print(f"\n[green]✓[/green] Added field: [cyan]{field_name}[/cyan]")


def _remove_field(fields: OrderedDict) -> None:
    """Remove a field."""
    if not fields:
        console.print("[yellow]No fields to remove[/yellow]")
        return
    
    console.print("\n[bold]Remove Field[/bold]")
    field_list = list(fields.keys())
    
    for i, name in enumerate(field_list, 1):
        console.print(f"  {i}. {name}")
    
    choice = Prompt.ask("\nField number to remove (or name)").strip()
    
    if choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(field_list):
            name = field_list[idx]
        else:
            console.print("[red]Invalid number[/red]")
            return
    else:
        name = choice
    
    if name in fields:
        del fields[name]
        console.print(f"[green]✓[/green] Removed: [cyan]{name}[/cyan]")
    else:
        console.print(f"[red]Field '{name}' not found[/red]")


def _edit_field(
    fields: OrderedDict,
    html: str | None,
    item_selector: str | None
) -> None:
    """Edit an existing field."""
    if not fields:
        console.print("[yellow]No fields to edit[/yellow]")
        return
    
    console.print("\n[bold]Edit Field[/bold]")
    field_list = list(fields.keys())
    
    for i, name in enumerate(field_list, 1):
        console.print(f"  {i}. {name}")
    
    choice = Prompt.ask("\nField number to edit (or name)").strip()
    
    if choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(field_list):
            name = field_list[idx]
        else:
            console.print("[red]Invalid number[/red]")
            return
    else:
        name = choice
    
    if name not in fields:
        console.print(f"[red]Field '{name}' not found[/red]")
        return
    
    field = fields[name]
    console.print(f"\n[bold]Editing:[/bold] [cyan]{name}[/cyan]")
    console.print(f"  Current selector: [green]{field.selector}[/green]")
    console.print(f"  Current attribute: [yellow]{field.attribute or '—'}[/yellow]")
    console.print(f"  Required: [magenta]{'Yes' if field.required else 'No'}[/magenta]")
    
    # What to edit?
    edit_choice = Prompt.ask(
        "\nWhat to edit?",
        choices=["selector", "attribute", "required", "rename", "cancel"],
        default="cancel"
    )
    
    if edit_choice == "selector":
        new_selector = Prompt.ask("New selector", default=field.selector).strip()
        if new_selector:
            fields[name] = FieldSchema(
                selector=new_selector,
                attribute=field.attribute,
                required=field.required
            )
            console.print(f"[green]✓[/green] Updated selector")
            
            # Preview
            if html and item_selector:
                console.print("\n[dim]Preview:[/dim]")
                _preview_single_field(html, item_selector, name, fields[name])
    
    elif edit_choice == "attribute":
        new_attr = Prompt.ask("New attribute (empty to clear)", default=field.attribute or "").strip()
        fields[name] = FieldSchema(
            selector=field.selector,
            attribute=new_attr if new_attr else None,
            required=field.required
        )
        console.print(f"[green]✓[/green] Updated attribute")
    
    elif edit_choice == "required":
        new_required = Confirm.ask("Required field?", default=field.required)
        fields[name] = FieldSchema(
            selector=field.selector,
            attribute=field.attribute,
            required=new_required
        )
        console.print(f"[green]✓[/green] Updated required flag")
    
    elif edit_choice == "rename":
        new_name = Prompt.ask("New field name", default=name).strip()
        if new_name and new_name != name:
            if new_name in fields:
                console.print(f"[red]Field '{new_name}' already exists[/red]")
            else:
                # Preserve order by reinserting
                items = list(fields.items())
                fields.clear()
                for k, v in items:
                    if k == name:
                        fields[new_name] = v
                    else:
                        fields[k] = v
                console.print(f"[green]✓[/green] Renamed to: [cyan]{new_name}[/cyan]")


def _reorder_fields(fields: OrderedDict) -> None:
    """Reorder fields."""
    if len(fields) < 2:
        console.print("[yellow]Need at least 2 fields to reorder[/yellow]")
        return
    
    console.print("\n[bold]Reorder Fields[/bold]")
    console.print("[dim]Enter new order as comma-separated numbers (e.g., 3,1,2)[/dim]\n")
    
    field_list = list(fields.keys())
    for i, name in enumerate(field_list, 1):
        console.print(f"  {i}. {name}")
    
    order = Prompt.ask("\nNew order").strip()
    
    try:
        indices = [int(x.strip()) - 1 for x in order.split(",")]
        
        if len(indices) != len(field_list) or len(set(indices)) != len(indices):
            console.print("[red]Invalid order (must use each number once)[/red]")
            return
        
        if not all(0 <= i < len(field_list) for i in indices):
            console.print("[red]Invalid numbers[/red]")
            return
        
        # Reorder
        items = [(field_list[i], fields[field_list[i]]) for i in indices]
        fields.clear()
        for k, v in items:
            fields[k] = v
        
        console.print("[green]✓[/green] Reordered")
        
    except ValueError:
        console.print("[red]Invalid format[/red]")


def _preview_extraction(
    html: str,
    item_selector: str,
    fields: dict[str, FieldSchema],
    limit: int = 3
) -> None:
    """Preview extraction for all fields."""
    console.print("\n[bold]Extraction Preview[/bold]")
    console.print(f"[dim]Showing first {limit} items[/dim]\n")
    
    try:
        soup = BeautifulSoup(html, 'html.parser')
        items = soup.select(item_selector)[:limit]
        
        if not items:
            console.print(f"[red]No items found with selector: {item_selector}[/red]")
            return
        
        for i, item in enumerate(items, 1):
            console.print(f"[bold cyan]Item {i}:[/bold cyan]")
            
            for field_name, field_schema in fields.items():
                try:
                    # Extract value
                    if field_schema.attribute:
                        # Attribute extraction
                        elem = item.select_one(field_schema.selector)
                        value = elem.get(field_schema.attribute, "") if elem else ""
                    else:
                        # Text extraction
                        elem = item.select_one(field_schema.selector)
                        value = elem.get_text(strip=True) if elem else ""
                    
                    # Truncate long values
                    display_value = value[:60] + "..." if len(str(value)) > 60 else value
                    console.print(f"  • [cyan]{field_name:15}[/cyan] {display_value or '[dim]empty[/dim]'}")
                    
                except Exception as e:
                    console.print(f"  • [cyan]{field_name:15}[/cyan] [red]Error: {e}[/red]")
            
            console.print()
    
    except Exception as e:
        console.print(f"[red]Preview error: {e}[/red]")


def _preview_single_field(
    html: str,
    item_selector: str,
    field_name: str,
    field_schema: FieldSchema,
    limit: int = 3
) -> None:
    """Preview single field extraction."""
    try:
        soup = BeautifulSoup(html, 'html.parser')
        items = soup.select(item_selector)[:limit]
        
        if not items:
            console.print(f"[red]No items found[/red]")
            return
        
        for i, item in enumerate(items, 1):
            try:
                if field_schema.attribute:
                    elem = item.select_one(field_schema.selector)
                    value = elem.get(field_schema.attribute, "") if elem else ""
                else:
                    elem = item.select_one(field_schema.selector)
                    value = elem.get_text(strip=True) if elem else ""
                
                display_value = value[:60] + "..." if len(str(value)) > 60 else value
                console.print(f"  {i}. {display_value or '[dim]empty[/dim]'}")
            except Exception as e:
                console.print(f"  {i}. [red]Error: {e}[/red]")
    
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


def _get_selector_suggestions(html: str, item_selector: str, limit: int = 20) -> list[tuple[str, str]]:
    """Get selector suggestions from HTML with preview text."""
    try:
        soup = BeautifulSoup(html, 'html.parser')
        items = soup.select(item_selector)
        
        if not items:
            return []
        
        sample = items[0]
        suggestions = []
        seen = set()
        
        # Common elements
        for tag in ['h1', 'h2', 'h3', 'h4', 'a', 'p', 'span', 'time', 'img']:
            elem = sample.select_one(tag)
            if elem and tag not in seen:
                preview = elem.get_text(strip=True)[:40] or elem.get('src', '')[:40] or elem.get('href', '')[:40]
                suggestions.append((tag, preview))
                seen.add(tag)
        
        # Class-based selectors
        for elem in sample.find_all():
            if elem.get('class'):
                for cls in elem['class'][:1]:  # Just first class
                    sel = f".{cls}"
                    if sel not in seen and len(suggestions) < limit:
                        preview = elem.get_text(strip=True)[:40]
                        suggestions.append((sel, preview))
                        seen.add(sel)
        
        return suggestions[:limit]
    
    except Exception:
        return []
