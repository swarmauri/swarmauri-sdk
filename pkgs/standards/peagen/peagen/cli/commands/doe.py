# peagen/commands/doe.py
"""
CLI wrapper for Design-of-Experiments expansion.
"""
from __future__ import annotations

import asyncio
import json
import uuid
import httpx
from pathlib import Path
from typing import Optional

import typer

from peagen.handlers.doe_handler import doe_handler
from peagen.handlers.doe_process_handler import doe_process_handler
from peagen.models import Status, Task

DEFAULT_GATEWAY = "http://localhost:8000/rpc"
local_doe_app = typer.Typer(help="Generate project-payload bundles from DOE specs.")
remote_doe_app = typer.Typer(help="Generate project-payload bundles from DOE specs.")

def _make_task(args: dict, action: str = "doe") -> Task:
    return Task(
        id=str(uuid.uuid4()),
        pool="default",
        action=action,
        status=Status.waiting,
        payload={"action": action, "args": args},
    )


# ───────────────────────────── local run ───────────────────────────────────
@local_doe_app.command("gen")
def run_gen(  # noqa: PLR0913
    ctx: typer.Context,
    spec: Path = typer.Argument(
        ..., exists=True, help="Path to the DOE specification YAML"
    ),
    template: Path = typer.Argument(
        ..., exists=True, help="Path to the project-payload template"
    ),
    output: Path = typer.Option(
        "project_payloads.yaml",
        "--output",
        "-o",
        help="Destination YAML file for generated payloads",
    ),
    config: Optional[Path] = typer.Option(
        None, "-c", "--config", help="Override configuration for this run"
    ),
    notify: Optional[str] = typer.Option(
        None, "--notify", help="Webhook URL for completion notification"
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Simulate the run without writing files"
    ),
    force: bool = typer.Option(
        False, "--force", help="Overwrite output even if it exists"
    ),
    skip_validate: bool = typer.Option(
        False, "--skip-validate", help="Skip validating the DOE spec"
    ),
    json_out: bool = typer.Option(
        False, "--json", help="Print the result dictionary as JSON"
    ),
) -> None:
    """Generate a project‑payload bundle from a DOE spec locally."""
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

    task = _make_task(args, action="doe")
    result = asyncio.run(doe_handler(task))

    if json_out:
        typer.echo(json.dumps(result, indent=2))
    else:
        outs = ", ".join(result.get("outputs", []))
        typer.echo(f"✅  {outs}")


# ─────────────────────────── remote submit ─────────────────────────────────
@remote_doe_app.command("gen")
def submit_gen(  # noqa: PLR0913
    ctx: typer.Context,
    spec: Path = typer.Argument(
        ..., exists=True, help="Path to the DOE specification YAML"
    ),
    template: Path = typer.Argument(
        ..., exists=True, help="Path to the project-payload template"
    ),
    output: Path = typer.Option(
        "project_payloads.yaml",
        "--output",
        "-o",
        help="Destination YAML file for generated payloads",
    ),
    config: Optional[Path] = typer.Option(
        None, "-c", "--config", help="Override configuration for this run"
    ),
    notify: Optional[str] = typer.Option(
        None, "--notify", help="Webhook URL for completion notification"
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Simulate the run without writing files"
    ),
    force: bool = typer.Option(
        False, "--force", help="Overwrite output even if it exists"
    ),
    skip_validate: bool = typer.Option(
        False, "--skip-validate", help="Skip validating the DOE spec"
    ),
) -> None:
    """Submit a DOE generation task to a remote worker."""
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
    task = _make_task(args, action="doe")

    rpc_req = {
        "jsonrpc": "2.0",
        "method": "Task.submit",
        "params": {"taskId": task.id, "pool": task.pool, "payload": task.payload},
    }

    with httpx.Client(timeout=30.0) as client:
        reply = client.post(ctx.obj.get("gateway_url"), json=rpc_req).json()

    if "error" in reply:
        typer.secho(
            f"Remote error {reply['error']['code']}: {reply['error']['message']}",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(1)

    typer.secho(f"Submitted task {task.id}", fg=typer.colors.GREEN)


# ───────────────────────────── local process ─────────────────────────────
@local_doe_app.command("process")
def run_process(  # noqa: PLR0913
    ctx: typer.Context,
    spec: Path = typer.Argument(
        ..., exists=True, help="Path to the DOE specification YAML"
    ),
    template: Path = typer.Argument(
        ..., exists=True, help="Path to the project-payload template"
    ),
    output: Path = typer.Option(
        "project_payloads.yaml",
        "--output",
        "-o",
        help="Destination YAML file for generated payloads",
    ),
    config: Optional[Path] = typer.Option(
        None, "-c", "--config", help="Override configuration for this run"
    ),
    notify: Optional[str] = typer.Option(
        None, "--notify", help="Webhook URL for completion notification"
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Simulate the run without writing files"
    ),
    force: bool = typer.Option(
        False, "--force", help="Overwrite output even if it exists"
    ),
    skip_validate: bool = typer.Option(
        False, "--skip-validate", help="Skip validating the DOE spec"
    ),
    json_out: bool = typer.Option(
        False, "--json", help="Print the result dictionary as JSON"
    ),
) -> None:
    """Process a DOE specification locally."""
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

    task = _make_task(args, action="doe_process")
    result = asyncio.run(doe_process_handler(task))

    typer.echo(json.dumps(result, indent=2) if json_out else json.dumps(result, indent=2))


# ───────────────────────────── remote process ────────────────────────────
@remote_doe_app.command("process")
def submit_process(  # noqa: PLR0913
    ctx: typer.Context,
    spec: Path = typer.Argument(
        ..., exists=True, help="Path to the DOE specification YAML"
    ),
    template: Path = typer.Argument(
        ..., exists=True, help="Path to the project-payload template"
    ),
    output: Path = typer.Option(
        "project_payloads.yaml",
        "--output",
        "-o",
        help="Destination YAML file for generated payloads",
    ),
    config: Optional[Path] = typer.Option(
        None, "-c", "--config", help="Override configuration for this run"
    ),
    notify: Optional[str] = typer.Option(
        None, "--notify", help="Webhook URL for completion notification"
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Simulate the run without writing files"
    ),
    force: bool = typer.Option(
        False, "--force", help="Overwrite output even if it exists"
    ),
    skip_validate: bool = typer.Option(
        False, "--skip-validate", help="Skip validating the DOE spec"
    ),
) -> None:
    """Enqueue DOE processing on a remote worker."""
    def _git_root(path: Path) -> Path:
        for p in [path] + list(path.parents):
            if (p / ".git").exists():
                return p
        return path

    root = _git_root(Path.cwd())

    def _canonical(p: Path) -> str:
        try:
            return str(p.resolve().relative_to(root))
        except ValueError:
            return str(p.resolve())

    args = {
        "spec": _canonical(spec),
        "template": _canonical(template),
        "output": str(output),
        "config": str(config) if config else None,
        "notify": notify,
        "dry_run": dry_run,
        "force": force,
        "skip_validate": skip_validate,
    }
    task = _make_task(args, action="doe_process")

    rpc_req = {
        "jsonrpc": "2.0",
        "method": "Task.submit",
        "params": {"taskId": task.id, "pool": task.pool, "payload": task.payload},
    }

    with httpx.Client(timeout=30.0) as client:
        reply = client.post(ctx.obj.get("gateway_url"), json=rpc_req).json()

    if "error" in reply:
        typer.secho(
            f"Remote error {reply['error']['code']}: {reply['error']['message']}",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(1)

    typer.secho(f"Submitted task {task.id}", fg=typer.colors.GREEN)
