# peagen/commands/doe.py
"""
CLI wrapper for Design-of-Experiments expansion.
"""
from __future__ import annotations

import asyncio, json, uuid, httpx
from pathlib import Path
from typing import Optional

import typer

from peagen.handlers.doe_handler import doe_handler
from peagen.models import Status, Task

DEFAULT_GATEWAY = "http://localhost:8000/rpc"
doe_app = typer.Typer(help="Generate project-payload bundles from DOE specs.")


def _make_task(args: dict) -> Task:
    return Task(
        id=str(uuid.uuid4()),
        pool="default",
        action="doe",
        status=Status.pending,
        payload={"args": args},
    )


# ───────────────────────────── local run ───────────────────────────────────
@doe_app.command("run")
def run(  # noqa: PLR0913
    spec: Path = typer.Argument(..., exists=True),
    template: Path = typer.Argument(..., exists=True),
    output: Path = typer.Option("project_payloads.yaml", "--output", "-o"),
    config: Optional[Path] = typer.Option(None, "-c", "--config"),
    notify: Optional[str] = typer.Option(None, "--notify"),
    dry_run: bool = typer.Option(False, "--dry-run"),
    force: bool = typer.Option(False, "--force"),
    skip_validate: bool = typer.Option(False, "--skip-validate"),
    json_out: bool = typer.Option(False, "--json"),
):
    args = {
        "spec": str(spec),
        "template": str(template),
        "output": str(output),
        "config": str(config) if config else None,
        "notify": notify,
        "dry_run": dry_run,
        "force": force,
        "skip_validate": skip_validate,
    }

    task = _make_task(args)
    result = asyncio.run(doe_handler(task))

    typer.echo(json.dumps(result, indent=2) if json_out else f"✅  {result['output']}")


# ─────────────────────────── remote submit ─────────────────────────────────
@doe_app.command("submit")
def submit(  # noqa: PLR0913
    spec: Path = typer.Argument(..., exists=True),
    template: Path = typer.Argument(..., exists=True),
    output: Path = typer.Option("project_payloads.yaml", "--output", "-o"),
    config: Optional[Path] = typer.Option(None, "-c", "--config"),
    notify: Optional[str] = typer.Option(None, "--notify"),
    dry_run: bool = typer.Option(False, "--dry-run"),
    force: bool = typer.Option(False, "--force"),
    skip_validate: bool = typer.Option(False, "--skip-validate"),
    gateway_url: str = typer.Option(
        DEFAULT_GATEWAY,
        "--gateway",
        envvar="PEAGEN_GATEWAY_URL",
    ),
):
    args = {
        "spec": str(spec),
        "template": str(template),
        "output": str(output),
        "config": str(config) if config else None,
        "notify": notify,
        "dry_run": dry_run,
        "force": force,
        "skip_validate": skip_validate,
    }
    task = _make_task(args)

    rpc_req = {
        "jsonrpc": "2.0",
        "id": task.id,
        "method": "Task.submit",
        "params": {"task": task.model_dump()},
    }

    with httpx.Client(timeout=30.0) as client:
        reply = client.post(gateway_url, json=rpc_req).json()

    if "error" in reply:
        typer.secho(
            f"Remote error {reply['error']['code']}: {reply['error']['message']}",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(1)

    typer.secho(f"Submitted task {task.id}", fg=typer.colors.GREEN)
