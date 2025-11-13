"""CLI interface for Forge tool."""

import sys
from pathlib import Path

import click

from scrapesuite.lib.schemas import load_schema
from .executor import ForgeExecutor, write_jsonl


@click.command()
@click.argument("schema_file", type=click.Path(exists=True))
@click.option(
    "--url", "-u",
    help="URL to extract from (overrides schema URL)"
)
@click.option(
    "--file", "-f",
    type=click.Path(exists=True),
    help="HTML file to extract from"
)
@click.option(
    "--output", "-o",
    type=click.Path(),
    default="output.jsonl",
    help="Output file path (default: output.jsonl)"
)
@click.option(
    "--max-pages",
    type=int,
    help="Maximum pages to fetch (for pagination)"
)
@click.option(
    "--no-metadata",
    is_flag=True,
    help="Don't include _meta field in output"
)
@click.option(
    "--pretty",
    is_flag=True,
    help="Pretty-print JSON output (not JSONL)"
)
def forge(schema_file, url, file, output, max_pages, no_metadata, pretty):
    """
    Execute extraction at scale using a schema.
    
    FORGE runs the extraction engine to pull structured data from web pages.
    It handles pagination, rate limiting, and exports to JSONL format.
    
    \b
    Examples:
      foundry forge schema.yml
      foundry forge schema.yml --url https://example.com
      foundry forge schema.yml --file page.html
      foundry forge schema.yml --max-pages 10 --output data.jsonl
      foundry forge schema.yml --no-metadata
    """
    # Load schema
    click.echo(f"📋 Loading schema: {schema_file}", err=True)
    try:
        schema = load_schema(schema_file)
    except Exception as e:
        click.echo(f"❌ Error loading schema: {e}", err=True)
        sys.exit(1)
    
    # Get HTML source
    html = None
    target_url = None
    
    if file:
        # Load from file
        click.echo(f"📄 Loading HTML from {file}...", err=True)
        try:
            html = Path(file).read_text(encoding="utf-8")
            target_url = f"file://{Path(file).absolute()}"
        except Exception as e:
            click.echo(f"❌ Error loading file: {e}", err=True)
            sys.exit(1)
    else:
        # Determine URL
        target_url = url or schema.url
        if not target_url:
            click.echo("❌ Error: No URL specified (use --url or set url in schema)", err=True)
            sys.exit(1)
    
    # Create executor
    executor = ForgeExecutor(schema)
    
    # Execute extraction
    try:
        if html:
            # Extract from provided HTML
            click.echo(f"🔨 Extracting from file...", err=True)
            items = executor.parser.parse(html)
            
            # Add metadata if requested
            if not no_metadata:
                for item in items:
                    item["_meta"] = {
                        "url": target_url,
                        "fetched_at": __import__('datetime').datetime.now().isoformat(),
                        "schema": schema.name,
                    }
            
            executor.stats["items_extracted"] = len(items)
            
        elif schema.pagination:
            click.echo(f"🔨 Extracting from {target_url} (with pagination)...", err=True)
            items = executor.fetch_with_pagination(
                target_url,
                max_pages=max_pages,
                include_metadata=not no_metadata
            )
        else:
            click.echo(f"🔨 Extracting from {target_url}...", err=True)
            items = executor.fetch_url(
                target_url,
                include_metadata=not no_metadata
            )
        
    except Exception as e:
        click.echo(f"❌ Extraction failed: {e}", err=True)
        sys.exit(1)
    
    # Write output
    if items:
        if pretty:
            # Pretty JSON (not JSONL)
            import json
            output_path = Path(output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with output_path.open("w", encoding="utf-8") as f:
                json.dump(items, f, indent=2, ensure_ascii=False)
            click.echo(f"✅ Wrote {len(items)} items to {output} (JSON)", err=True)
        else:
            # JSONL format
            count = write_jsonl(items, output)
            click.echo(f"✅ Wrote {count} items to {output} (JSONL)", err=True)
        
        # Show stats
        stats = executor.get_stats()
        click.echo(f"\n📊 Statistics:", err=True)
        click.echo(f"   URLs fetched: {stats['urls_fetched']}", err=True)
        click.echo(f"   Items extracted: {stats['items_extracted']}", err=True)
        if stats['errors'] > 0:
            click.echo(f"   Errors: {stats['errors']}", err=True)
    else:
        click.echo("⚠️  No items extracted", err=True)


if __name__ == "__main__":
    forge()
