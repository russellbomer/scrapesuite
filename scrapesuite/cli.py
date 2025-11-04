"""CLI interface for ScrapeSuite."""

import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from scrapesuite.core import load_yaml, run_job
from scrapesuite.state import open_db
from scrapesuite.wizard import run_wizard

app = typer.Typer()
console = Console()


@app.command()
def init() -> None:
    """Run interactive wizard to create a new job YAML."""
    try:
        run_wizard()
    except KeyboardInterrupt:
        console.print("\n[yellow]Cancelled[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@app.command()
def run(
    job_yaml: str,
    max_items: int = typer.Option(200, "--max-items", "-n"),
    offline: bool = typer.Option(True, "--offline/--live"),
    db: str | None = typer.Option(None, "--db", help="SQLite database path"),
    timezone: str = typer.Option("America/New_York", "--timezone", "-tz"),
) -> None:
    """Run a single job from YAML file."""
    try:
        job_dict = load_yaml(job_yaml)
        df, next_cursor = run_job(
            job_dict,
            max_items=max_items,
            offline=offline,
            db_path=db,
            timezone=timezone,
        )

        # Count new items (first_seen = last_seen means newly inserted)
        conn = open_db(db)
        cursor_row = conn.execute(
            "SELECT COUNT(*) as count FROM items WHERE job = ? AND first_seen = last_seen",
            (job_dict["job"],),
        ).fetchone()
        new_count = cursor_row["count"] if cursor_row else 0
        conn.close()

        summary = (
            f"{job_dict['job']}: {new_count} new, {len(df)} in batch, next_cursor={next_cursor}"
        )
        console.print(f"[green]{summary}[/green]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@app.command("run-all")
def run_all(
    max_items: int = typer.Option(200, "--max-items", "-n"),
    offline: bool = typer.Option(True, "--offline/--live"),
    db: str | None = typer.Option(None, "--db", help="SQLite database path"),
    timezone: str = typer.Option("America/New_York", "--timezone", "-tz"),
) -> None:
    """Run all jobs in the jobs/ directory."""
    jobs_dir = Path("jobs")
    if not jobs_dir.exists():
        console.print("[red]jobs/ directory not found[/red]")
        sys.exit(1)

    yaml_files = sorted(jobs_dir.glob("*.yml"))
    if not yaml_files:
        console.print("[yellow]No job YAML files found[/yellow]")
        return

    for yaml_file in yaml_files:
        try:
            job_dict = load_yaml(str(yaml_file))
            df, next_cursor = run_job(
                job_dict,
                max_items=max_items,
                offline=offline,
                db_path=db,
                timezone=timezone,
            )

            conn = open_db(db)
            cursor_row = conn.execute(
                "SELECT COUNT(*) as count FROM items WHERE job = ? AND first_seen = last_seen",
                (job_dict["job"],),
            ).fetchone()
            new_count = cursor_row["count"] if cursor_row else 0
            conn.close()

            summary = (
                f"{job_dict['job']}: {new_count} new, {len(df)} in batch, next_cursor={next_cursor}"
            )
            console.print(f"[green]{summary}[/green]")
        except Exception as e:
            console.print(f"[red]Error in {yaml_file}: {e}[/red]")
            continue


@app.command()
def state(
    db: str | None = typer.Option(None, "--db", help="SQLite database path"),
) -> None:
    """Show job state (last cursor and last run time)."""
    try:
        conn = open_db(db)
        rows = conn.execute(
            "SELECT job, last_cursor, last_run FROM jobs_state ORDER BY job"
        ).fetchall()
        conn.close()

        if not rows:
            console.print("[yellow]No job state found[/yellow]")
            return

        table = Table(title="Job State")
        table.add_column("Job", style="cyan")
        table.add_column("Last Cursor", style="green")
        table.add_column("Last Run", style="yellow")

        for row in rows:
            table.add_row(
                row["job"] or "",
                row["last_cursor"] or "(none)",
                row["last_run"] or "(never)",
            )

        console.print(table)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    app()
