# peagen/commands/validate.py

import asyncio
from typing import Any, Dict

import typer

from peagen.handlers.validate_handler import validate_handler
from peagen.cli.task_helpers import build_task, submit_task

local_validate_app = typer.Typer(help="Validate Peagen artifacts.")
remote_validate_app = typer.Typer(help="Validate Peagen artifacts via JSON-RPC.")

# ────────────────────────────── local validate ────────────────────────────────────


@local_validate_app.command("validate")
def run_validate(
    ctx: typer.Context,
    kind: str = typer.Argument(
        ...,
        help="Kind of artifact to validate (config, doe, evolve, ptree, projects_payload).",
    ),
    path: str = typer.Option(
        None, help="Path to the file to validate (not required for config)."
    ),
    repo: str = typer.Option(..., "--repo", help="Git repository URI"),
    ref: str = typer.Option("HEAD", "--ref", help="Git ref or commit SHA"),
):
    """
    Run validation locally (no queue) by constructing a Task model
    and invoking the same handler that a worker would use.
    """
    # 1) Create a Task instance with default status/result
    args: Dict[str, Any] = {
        "kind": kind,
        "path": path,
    }
    if repo:
        args.update({"repo": repo, "ref": ref})
    task = build_task("validate", args, pool="default")

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


@remote_validate_app.command("validate")
def submit_validate(
    ctx: typer.Context,
    kind: str = typer.Argument(
        ...,
        help="Kind of artifact to validate (config, doe, ptree, projects_payload).",
    ),
    path: str = typer.Option(
        None, help="Path to the file to validate (not required for config)."
    ),
    repo: str = typer.Option(..., "--repo", help="Git repository URI"),
    ref: str = typer.Option("HEAD", "--ref", help="Git ref or commit SHA"),
):
    """
    Submit this validation as a background task. Returns immediately with a taskId.
    """
    # 1) Create a Task instance
    args: Dict[str, Any] = {
        "kind": kind,
        "path": path,
    }
    if repo:
        args.update({"repo": repo, "ref": ref})
    task = build_task("validate", args, pool=ctx.obj.get("pool", "default"))

    # 2) Build Task.submit envelope using Task fields
    try:
        reply = submit_task(ctx.obj["rpc"], task)
        if "error" in reply:
            typer.echo(f"[ERROR] {reply['error']['message']}")
            raise typer.Exit(1)
        typer.echo(f"Submitted validation → taskId={reply['result']['taskId']}")
    except Exception as exc:
        typer.echo(f"[ERROR] Could not reach gateway: {exc}")
        raise typer.Exit(1)
