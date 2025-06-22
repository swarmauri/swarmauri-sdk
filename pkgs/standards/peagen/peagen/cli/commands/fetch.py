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
local_fetch_app = typer.Typer(help="Materialise Peagen workspaces from URIs.")
remote_fetch_app = typer.Typer(help="Materialise Peagen workspaces from URIs.")


# ───────────────────────── helpers ─────────────────────────
def _build_task(args: dict) -> Task:
    """Construct a Task with the fetch action embedded in the payload."""
    return Task(
        id=str(uuid.uuid4()),
        pool="default",
        status=Status.waiting,
        payload={"action": "fetch", "args": args},
    )


def _collect_args(
    workspaces: List[str],
    no_source: bool,
    install_template_sets_flag: bool,
    repo: Optional[str] = None,
    ref: str = "HEAD",
) -> dict:
    if repo:
        workspaces = [f"git+{repo}@{ref}"]

    return {
        "workspaces": workspaces,
        "out_dir": str(Path.cwd()),
        "no_source": no_source,
        "install_template_sets": install_template_sets_flag,
    }


# ───────────────────────── local run ───────────────────────
@local_fetch_app.command("fetch")
def run(
    ctx: typer.Context,
    workspaces: Optional[List[str]] = typer.Argument(None, help="Workspace URI(s)"),
    no_source: bool = typer.Option(
        False, "--no-source/--with-source", help="Skip cloning source packages"
    ),
    install_template_sets_flag: bool = typer.Option(
        True,
        "--install-template-sets/--no-install-template-sets",
        help="Install template sets referenced by the workspace descriptor",
    ),
    repo: Optional[str] = typer.Option(None, "--repo", help="Git repository URI"),
    ref: str = typer.Option("HEAD", "--ref", help="Git ref or commit SHA"),
):
    """Synchronously build the workspace on this machine."""
    args = _collect_args(
        workspaces or [], no_source, install_template_sets_flag, repo, ref
    )
    task = _build_task(args)

    result = asyncio.run(fetch_handler(task))
    typer.echo(json.dumps(result, indent=2))


# ────────────────────── remote submission ──────────────────
@remote_fetch_app.command("fetch")
def submit(
    ctx: typer.Context,
    workspaces: Optional[List[str]] = typer.Argument(None, help="Workspace URI(s)"),
    no_source: bool = typer.Option(
        False, "--no-source/--with-source", help="Skip cloning source packages"
    ),
    install_template_sets_flag: bool = typer.Option(
        True,
        "--install-template-sets/--no-install-template-sets",
        help="Install template sets referenced by the workspace descriptor",
    ),
    repo: Optional[str] = typer.Option(None, "--repo", help="Git repository URI"),
    ref: str = typer.Option("HEAD", "--ref", help="Git ref or commit SHA"),
):
    """Enqueue the fetch task on a worker farm and return immediately."""
    args = _collect_args(
        workspaces or [], no_source, install_template_sets_flag, repo, ref
    )
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
