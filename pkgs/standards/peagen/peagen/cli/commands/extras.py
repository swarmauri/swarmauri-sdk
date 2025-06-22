"""Generate EXTRAS schemas via CLI."""

from __future__ import annotations

import asyncio
import uuid
from pathlib import Path
from typing import Any, Dict, Optional

import typer

from peagen.handlers.extras_handler import extras_handler
from peagen.models import Task
from swarmauri_standard.loggers.Logger import Logger

local_extras_app = typer.Typer(help="Manage EXTRAS schemas.")
remote_extras_app = typer.Typer(help="Manage EXTRAS schemas remotely.")


def _build_task(args: Dict[str, Any]) -> Task:
    return Task(
        id=str(uuid.uuid4()), pool="default", payload={"action": "extras", "args": args}
    )


@local_extras_app.command("extras")
def run_extras(
    templates_root: Optional[Path] = typer.Option(
        None, "--templates-root", help="Directory containing template sets"
    ),
    schemas_dir: Optional[Path] = typer.Option(
        None, "--schemas-dir", help="Destination for generated schema files"
    ),
) -> None:
    """Run EXTRAS generation locally."""
    logger = Logger(name="extras locally")
    logger.logger.info("Entering local extras command")

    args = {
        "templates_root": str(templates_root.expanduser()) if templates_root else None,
        "schemas_dir": str(schemas_dir.expanduser()) if schemas_dir else None,
    }
    task = _build_task(args)

    try:
        result: Dict[str, Any] = asyncio.run(extras_handler(task))
    except Exception as exc:
        typer.echo(f"[ERROR] Exception inside extras_handler: {exc}")
        raise typer.Exit(1)

    for path in result.get("generated", []):
        typer.echo(f"✅ Wrote {path}")

    logger.logger.info("Exiting extras_run command")


@remote_extras_app.command("extras")
def submit_extras(
    ctx: typer.Context,
    templates_root: Optional[Path] = typer.Option(
        None, "--templates-root", help="Directory containing template sets"
    ),
    schemas_dir: Optional[Path] = typer.Option(
        None, "--schemas-dir", help="Destination for generated schema files"
    ),
) -> None:
    """Submit EXTRAS schema generation as a background task."""
    args = {
        "templates_root": str(templates_root.expanduser()) if templates_root else None,
        "schemas_dir": str(schemas_dir.expanduser()) if schemas_dir else None,
    }
    task = _build_task(args)
    gateway_url = ctx.obj.get("gateway_url")

    envelope = {
        "jsonrpc": "2.0",
        "method": "Task.submit",
        "params": {
            "pool": task.pool,
            "payload": task.payload,
        },
    }

    try:
        import httpx

        resp = httpx.post(gateway_url, json=envelope, timeout=10.0)
        resp.raise_for_status()
        data = resp.json()
        if data.get("error"):
            typer.echo(f"[ERROR] {data['error']}")
            raise typer.Exit(1)
        typer.echo(f"Submitted extras generation → taskId={data['id']}")
    except Exception as exc:
        typer.echo(f"[ERROR] Could not reach gateway at {gateway_url}: {exc}")
        raise typer.Exit(1)
