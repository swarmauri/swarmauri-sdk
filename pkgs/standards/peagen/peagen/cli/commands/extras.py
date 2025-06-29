"""Generate EXTRAS schemas via CLI."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any, Dict, Optional

import typer
from functools import partial

from peagen.handlers.extras_handler import extras_handler
from swarmauri_standard.loggers.Logger import Logger
from peagen.transport import TASK_SUBMIT
from peagen.transport.jsonrpc_schemas.task import SubmitParams, SubmitResult
from peagen.cli.rpc_utils import rpc_post
from peagen.cli.task_builder import _build_task as _generic_build_task

local_extras_app = typer.Typer(help="Manage EXTRAS schemas.")
remote_extras_app = typer.Typer(help="Manage EXTRAS schemas remotely.")


_build_task = partial(_generic_build_task, "extras")


@local_extras_app.command("extras")
def run_extras(
    ctx: typer.Context,
    templates_root: Optional[Path] = typer.Option(
        None, "--templates-root", help="Directory containing template sets"
    ),
    schemas_dir: Optional[Path] = typer.Option(
        None, "--schemas-dir", help="Destination for generated schema files"
    ),
    repo: str = typer.Option(..., "--repo", help="Git repository URI"),
    ref: str = typer.Option("HEAD", "--ref", help="Git ref or commit SHA"),
) -> None:
    """Run EXTRAS generation locally."""
    logger = Logger(name="extras locally")
    logger.logger.info("Entering local extras command")

    args = {
        "templates_root": str(templates_root.expanduser()) if templates_root else None,
        "schemas_dir": str(schemas_dir.expanduser()) if schemas_dir else None,
    }
    if repo:
        args.update({"repo": repo, "ref": ref})
    task = _build_task(args, ctx.obj.get("pool", "default"))

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
    repo: str = typer.Option(..., "--repo", help="Git repository URI"),
    ref: str = typer.Option("HEAD", "--ref", help="Git ref or commit SHA"),
    gateway_url: str = typer.Option(
        "http://localhost:8000/rpc", "--gateway-url", help="JSON-RPC gateway endpoint"
    ),
) -> None:
    """Submit EXTRAS schema generation as a background task."""
    args = {
        "templates_root": str(templates_root.expanduser()) if templates_root else None,
        "schemas_dir": str(schemas_dir.expanduser()) if schemas_dir else None,
    }
    if repo:
        args.update({"repo": repo, "ref": ref})
    task = _build_task(args, ctx.obj.get("pool", "default"))

    try:
        reply = rpc_post(
            gateway_url,
            TASK_SUBMIT,
            SubmitParams(task=task).model_dump(),
            timeout=10.0,
            result_model=SubmitResult,
        )
        if reply.error:
            typer.echo(f"[ERROR] {reply.error.message}")
            raise typer.Exit(1)
        typer.echo(f"Submitted extras generation → taskId={reply.result.taskId}")
    except Exception as exc:
        typer.echo(f"[ERROR] Could not reach gateway at {gateway_url}: {exc}")
        raise typer.Exit(1)
