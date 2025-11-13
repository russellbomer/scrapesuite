"""Output formatting for Probe tool."""

import json
from typing import Any


def format_as_json(analysis: dict[str, Any], pretty: bool = True) -> str:
    """
    Format analysis as JSON.
    
    Args:
        analysis: Analysis result from analyze_page()
        pretty: Whether to pretty-print (default True)
    
    Returns:
        JSON string
    """
    if pretty:
        return json.dumps(analysis, indent=2, ensure_ascii=False)
    return json.dumps(analysis, ensure_ascii=False)


def format_as_terminal(analysis: dict[str, Any]) -> str:
    """
    Format analysis for terminal output with colors and structure.
    
    Args:
        analysis: Analysis result from analyze_page()
    
    Returns:
        Formatted string for terminal display
    """
    try:
        from rich.console import Console
        from rich.panel import Panel
        from rich.table import Table
        from rich import box
        
        console = Console()
        
        # Create output buffer
        from io import StringIO
        output = StringIO()
        console = Console(file=output, width=120)
        
        # Header
        url = analysis.get("url", "Unknown")
        console.print(f"\n[bold cyan]🔍 Probe Analysis Results[/bold cyan]")
        if url:
            console.print(f"[dim]URL: {url}[/dim]\n")
        
        # Metadata section
        metadata = analysis.get("metadata", {})
        if metadata.get("title"):
            console.print(Panel(
                f"[bold]{metadata['title']}[/bold]\n"
                f"{metadata.get('description', '')}",
                title="Page Metadata",
                border_style="blue"
            ))
        
        # Framework detection
        frameworks = analysis.get("frameworks", [])
        if frameworks:
            table = Table(title="Detected Frameworks", box=box.ROUNDED, show_header=True)
            table.add_column("Framework", style="cyan")
            table.add_column("Confidence", style="green", justify="right")
            table.add_column("Version", style="yellow")
            
            for fw in frameworks[:5]:  # Top 5
                conf_pct = f"{fw['confidence'] * 100:.1f}%"
                version = fw.get("version") or "—"
                table.add_row(fw["name"], conf_pct, version)
            
            console.print(table)
            console.print()
        
        # Containers (item patterns)
        containers = analysis.get("containers", [])
        if containers:
            table = Table(title="Detected Item Containers", box=box.ROUNDED, show_header=True)
            table.add_column("Selector", style="magenta", max_width=50)
            table.add_column("Items", style="green", justify="right")
            table.add_column("Sample", style="dim", max_width=40)
            
            for cont in containers[:5]:  # Top 5
                selector = cont.get("child_selector", cont.get("selector", ""))
                count = str(cont.get("item_count", 0))
                sample = cont.get("sample_text", "")[:40]
                table.add_row(selector, count, sample)
            
            console.print(table)
            console.print()
        
        # Suggestions
        suggestions = analysis.get("suggestions", {})
        if suggestions.get("best_container"):
            best = suggestions["best_container"]
            console.print(Panel(
                f"[bold green]✓ Best Container[/bold green]\n"
                f"Selector: [cyan]{best.get('child_selector')}[/cyan]\n"
                f"Items: [yellow]{best.get('item_count')}[/yellow]",
                border_style="green"
            ))
        
        # Field suggestions
        field_candidates = suggestions.get("field_candidates", [])
        if field_candidates:
            table = Table(title="Suggested Fields", box=box.SIMPLE, show_header=True)
            table.add_column("Field", style="yellow")
            table.add_column("Selector", style="cyan")
            table.add_column("Sample", style="dim", max_width=30)
            
            for field in field_candidates[:8]:  # Top 8
                table.add_row(
                    field.get("name", ""),
                    field.get("selector", ""),
                    field.get("sample", "")[:30]
                )
            
            console.print(table)
            console.print()
        
        # Framework hint
        if suggestions.get("framework_hint"):
            hint = suggestions["framework_hint"]
            console.print(Panel(
                f"[bold]{hint['name']}[/bold] detected\n"
                f"{hint['recommendation']}",
                title="💡 Framework Hint",
                border_style="yellow"
            ))
        
        # Statistics
        stats = analysis.get("statistics", {})
        if stats:
            console.print("\n[bold]📊 Page Statistics[/bold]")
            console.print(f"  Elements: {stats.get('total_elements', 0):,}")
            console.print(f"  Links: {stats.get('total_links', 0):,}")
            console.print(f"  Images: {stats.get('total_images', 0):,}")
            console.print(f"  Text: {stats.get('text_words', 0):,} words\n")
        
        return output.getvalue()
        
    except ImportError:
        # Fallback to simple text if rich is not available
        return _format_as_simple_text(analysis)


def _format_as_simple_text(analysis: dict[str, Any]) -> str:
    """Fallback formatter without rich library."""
    lines = []
    lines.append("\n=== Probe Analysis Results ===\n")
    
    url = analysis.get("url")
    if url:
        lines.append(f"URL: {url}\n")
    
    # Metadata
    metadata = analysis.get("metadata", {})
    if metadata.get("title"):
        lines.append(f"\nTitle: {metadata['title']}")
        if metadata.get("description"):
            lines.append(f"Description: {metadata['description']}\n")
    
    # Frameworks
    frameworks = analysis.get("frameworks", [])
    if frameworks:
        lines.append("\n--- Detected Frameworks ---")
        for fw in frameworks[:5]:
            conf = f"{fw['confidence'] * 100:.1f}%"
            version = fw.get("version") or "unknown"
            lines.append(f"  • {fw['name']} ({conf}) - v{version}")
    
    # Containers
    containers = analysis.get("containers", [])
    if containers:
        lines.append("\n--- Item Containers ---")
        for cont in containers[:5]:
            selector = cont.get("child_selector", "")
            count = cont.get("item_count", 0)
            lines.append(f"  • {selector} ({count} items)")
    
    # Suggestions
    suggestions = analysis.get("suggestions", {})
    if suggestions.get("item_selector"):
        lines.append(f"\n--- Suggestion ---")
        lines.append(f"Best selector: {suggestions['item_selector']}")
    
    # Stats
    stats = analysis.get("statistics", {})
    if stats:
        lines.append(f"\n--- Statistics ---")
        lines.append(f"  Elements: {stats.get('total_elements', 0):,}")
        lines.append(f"  Links: {stats.get('total_links', 0):,}")
        lines.append(f"  Images: {stats.get('total_images', 0):,}")
    
    lines.append("\n")
    return "\n".join(lines)
