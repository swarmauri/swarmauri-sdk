from __future__ import annotations

import typer

from peagen.queue import make_queue

recover_app = typer.Typer(help="Crash recovery utilities")


@recover_app.command("orphans")
def requeue_orphans(
    queue_url: str = typer.Option(..., "--queue-url"),
    idle_ms: int = typer.Option(60000, "--idle-ms"),
    max_batch: int = typer.Option(50, "--max-batch"),
) -> None:
    """Requeue orphaned tasks from the message broker."""
    provider = "redis" if queue_url.startswith("redis") else "stub"
    queue = make_queue(provider, url=queue_url)
    moved = queue.requeue_orphans(idle_ms, max_batch)
    typer.echo(f"moved {moved} orphan tasks")

