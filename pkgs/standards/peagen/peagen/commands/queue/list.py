from __future__ import annotations

import os
import typer

from peagen.cli_common import global_cli_options
from peagen.queue import make_queue

list_app = typer.Typer(help="List queue information", invoke_without_command=True)


@list_app.callback(invoke_without_command=True)
@global_cli_options
def list_pending_cmd(
    ctx: typer.Context,
    limit: int = typer.Option(100, "--limit", "-n", help="Number of tasks to show"),
) -> None:
    """Show pending tasks in the queue."""
    queue_url = os.environ.get("QUEUE_URL", "stub://")
    provider = "redis" if queue_url.startswith("redis") else "stub"
    queue = make_queue(provider, url=queue_url)
    tasks = list(getattr(queue, "list_pending", lambda *_: [])(limit))
    if not tasks:
        typer.echo("No pending tasks")
        return
    for t in tasks:
        requires = ",".join(sorted(t.requires)) if getattr(t, "requires", None) else ""
        typer.echo(f"{t.id}\t{t.kind}\t{requires}")
