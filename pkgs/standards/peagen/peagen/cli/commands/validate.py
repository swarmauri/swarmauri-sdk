# peagen/commands/validate.py

import asyncio
import uuid
from typing import Any, Dict

import typer

from peagen.handlers.validate_handler import validate_handler
from peagen.models import Task

local_validate_app = typer.Typer()


@local_validate_app.command("run")
def run_validate(
    ctx: typer.Context,
    kind: str = typer.Argument(
        ...,
        help="Kind of artifact to validate (config, doe, manifest, ptree, projects_payload).",
    ),
    path: str = typer.Option(
        None, help="Path to the file to validate (not required for config)."
    ),
):
    """
    Run validation locally (no queue) by constructing a Task model
    and invoking the same handler that a worker would use.
    """
    # 1) Create a Task instance with default status/result
    task_id = str(uuid.uuid4())
    args: Dict[str, Any] = {
        "kind": kind,
        "path": path,
    }
    task = Task(
        id=task_id,
        pool="default",
        payload={"action": "validate", "args": args},
    )

    # 2) Call validate_handler(task) via asyncio.run
    try:
        result: Dict[str, Any] = asyncio.run(validate_handler(task))
    except Exception as exc:
        typer.echo(f"[ERROR] Exception inside validate_handler: {exc}")
        raise typer.Exit(1)

    # 3) Inspect the returned dict
    if not result.get("ok", False):
        typer.echo(f"❌  Invalid {kind}:", err=True)
        for error in result.get("errors", []):
            typer.echo(f"   • {error}", err=True)
        raise typer.Exit(1)
    else:
        typer.echo(f"✅  {kind.capitalize()} is valid.")


@local_validate_app.command("submit")
def submit_validate(
    ctx: typer.Context,
    kind: str = typer.Argument(
        ...,
        help="Kind of artifact to validate (config, doe, manifest, ptree, projects_payload).",
    ),
    path: str = typer.Option(
        None, help="Path to the file to validate (not required for config)."
    ),
    gateway_url: str = typer.Option(
        "http://localhost:8000/rpc", "--gateway-url", help="JSON-RPC gateway endpoint"
    ),
):
    """
    Submit this validation as a background task. Returns immediately with a taskId.
    """
    # 1) Create a Task instance
    task_id = str(uuid.uuid4())
    args: Dict[str, Any] = {
        "kind": kind,
        "path": path,
    }
    task = Task(
        id=task_id,
        pool="default",
        payload={"action": "validate", "args": args},
    )

    # 2) Build Work.start envelope using Task fields
    envelope = {
        "jsonrpc": "2.0",
        "id": str(uuid.uuid4()),
        "method": "Work.start",
        "params": {
            "id": task.id,
            "pool": task.pool,
            "payload": task.payload,
        },
    }

    # 3) POST to gateway
    try:
        import httpx

        resp = httpx.post(gateway_url, json=envelope, timeout=10.0)
        resp.raise_for_status()
        data = resp.json()
        if data.get("error"):
            typer.echo(f"[ERROR] {data['error']}")
            raise typer.Exit(1)
        typer.echo(f"Submitted validation → taskId={task.id}")
    except Exception as exc:
        typer.echo(f"[ERROR] Could not reach gateway at {gateway_url}: {exc}")
        raise typer.Exit(1)
