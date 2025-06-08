"""
CLI wrapper for querying asynchronous tasks.
"""

from __future__ import annotations

import json
import time
import uuid

import httpx
import typer

remote_task_app = typer.Typer(help="Inspect asynchronous tasks.")


@remote_task_app.command("get")
def get(  # noqa: D401
    ctx: typer.Context,
    task_id: str = typer.Argument(..., help="UUID of the task to query"),
    watch: bool = typer.Option(False, "--watch", "-w", help="Poll until finished"),
    interval: float = typer.Option(
        2.0, "--interval", "-i", help="Seconds between polls"
    ),
):
    """Fetch status / result for *TASK_ID* (optionally watch until done)."""

    def _rpc_call() -> dict:
        req = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "Task.get",
            "params": {"taskId": task_id},
        }
        res = httpx.post(ctx.obj.get("gateway_url"), json=req, timeout=30.0).json()
        return res["result"]

    while True:
        reply = _rpc_call()
        typer.echo(json.dumps(reply, indent=2))

        if not watch or reply["status"] in {"finished", "failed"}:
            break
        time.sleep(interval)


@remote_task_app.command("control")
def control(
    ctx: typer.Context,
    action: str = typer.Argument(..., help="control action"),
    label: str = typer.Argument(..., help="target label"),
):
    """Send a control-plane command."""
    req = {
        "jsonrpc": "2.0",
        "id": str(uuid.uuid4()),
        "method": f"Control.{action}",
        "params": {"label": label},
    }
    resp = httpx.post(ctx.obj.get("gateway_url"), json=req, timeout=30.0).json()
    typer.echo(json.dumps(resp, indent=2))
