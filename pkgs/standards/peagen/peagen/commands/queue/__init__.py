from __future__ import annotations

import typer

import os
from .dlq import dlq_app
from peagen.queue import make_queue
from peagen.cli_common import global_cli_options

queue_app = typer.Typer(help="Queue utilities")
queue_app.add_typer(dlq_app, name="dlq")


@queue_app.command("list", help="List pending tasks in the queue.")
@global_cli_options
def list_tasks_cmd(
    ctx: typer.Context,
    limit: int = typer.Option(10, "--limit", "-n", help="Number of tasks to show"),
    offset: int = typer.Option(0, "--offset", help="Skip this many tasks"),
) -> None:
    queue_url = os.environ.get("QUEUE_URL", "stub://")
    provider = "redis" if queue_url.startswith("redis") else "stub"
    queue = make_queue(provider, url=queue_url)
    tasks = []
    if hasattr(queue, "list_tasks"):
        tasks = queue.list_tasks(limit, offset)
    if not tasks:
        typer.echo("No pending tasks")
        return
    typer.echo("ID\tKIND\tATTEMPTS")
    for t in tasks:
        typer.echo(f"{t.id}\t{t.kind}\t{t.attempts}")

__all__ = ["queue_app"]
