# peagen/commands/fetch.py
"""
CLI front-end for workspace reconstruction.

Sub-commands
------------
fetch run     – local, blocking execution
fetch submit  – enqueue via JSON-RPC gateway
"""

from __future__ import annotations

import asyncio
import json
import uuid
from pathlib import Path
from typing import List, Optional

import httpx
import typer

from peagen.handlers.fetch_handler import fetch_handler
from peagen.models import Status, Task

DEFAULT_GATEWAY = "http://localhost:8000/rpc"
local_fetch_app = typer.Typer(help="Reconstruct Peagen workspaces from manifest(s).")
remote_fetch_app = typer.Typer(help="Reconstruct Peagen workspaces from manifest(s).")

# ───────────────────────── helpers ─────────────────────────
def _build_task(args: dict) -> Task:
    return Task(
        id=str(uuid.uuid4()),
        pool="default",
        action="fetch",
        status=Status.waiting,
        payload={"args": args},
    )


def _collect_args(
    manifests: List[str],
    out_dir: Optional[Path],
    no_source: bool,
    install_template_sets_flag: bool,
) -> dict:
    return {
        "manifests": manifests,
        "out_dir": str(out_dir.expanduser()) if out_dir else None,
        "no_source": no_source,
        "install_template_sets": install_template_sets_flag,
    }


# ───────────────────────── local run ───────────────────────
@local_fetch_app.command("fetch")
def run(
    ctx: typer.Context,
    manifests: List[str] = typer.Argument(..., help="Manifest JSON URI(s)"),
    out_dir: Optional[Path] = typer.Option(
        None, "--out", "-o", help="Destination folder (temp dir if omitted)"
    ),
    no_source: bool = typer.Option(
        False, "--no-source/--with-source", help="Skip cloning source packages"
    ),
    install_template_sets_flag: bool = typer.Option(
        True,
        "--install-template-sets/--no-install-template-sets",
        help="Install template sets referenced by the manifest(s)",
    ),
):
    """Synchronously build the workspace on this machine."""
    args = _collect_args(manifests, out_dir, no_source, install_template_sets_flag)
    task = _build_task(args)

    result = asyncio.run(fetch_handler(task))
    typer.echo(json.dumps(result, indent=2))


# ────────────────────── remote submission ──────────────────
@remote_fetch_app.command("fetch")
def submit(
    ctx: typer.Context,
    manifests: List[str] = typer.Argument(
        ..., help="Manifest JSON URI(s)"
    ),
    out_dir: Optional[Path] = typer.Option(
        None, "--out", "-o", help="Destination folder on the worker"
    ),
    no_source: bool = typer.Option(
        False, "--no-source/--with-source", help="Skip cloning source packages"
    ),
    install_template_sets_flag: bool = typer.Option(
        True,
        "--install-template-sets/--no-install-template-sets",
        help="Install template sets referenced by the manifest(s)",
    )
):
    """Enqueue the fetch task on a worker farm and return immediately."""
    args = _collect_args(manifests, out_dir, no_source, install_template_sets_flag)
    task = _build_task(args)

    rpc_req = {
        "jsonrpc": "2.0",
        "id": task.id,
        "method": "Task.submit",
        "params": {"taskId": task.id, "pool": task.pool, "payload": task.payload},
    }

    with httpx.Client(timeout=30.0) as client:
        resp = client.post(ctx.obj.get("gateway_url"), json=rpc_req)
        resp.raise_for_status()
        reply = resp.json()

    if "error" in reply:
        typer.secho(
            f"Remote error {reply['error']['code']}: {reply['error']['message']}",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(code=1)

    typer.secho(f"Submitted task {task.id}", fg=typer.colors.GREEN)
    if reply.get("result"):
        typer.echo(json.dumps(reply["result"], indent=2))
