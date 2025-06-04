"""Validate manifests and configuration files."""
from __future__ import annotations

import asyncio
import json
import uuid
from pathlib import Path
from typing import Optional

import httpx
import typer

from peagen.handlers.validate_handler import validate_handler
from peagen.models import Status, Task

DEFAULT_GATEWAY = "http://localhost:8000/rpc"
VALID_KINDS = ["config", "doe", "manifest", "ptree", "projects_payload"]

validate_app = typer.Typer(help="Validation utilities for Peagen artefacts.")


def _build_task(args: dict) -> Task:
    return Task(
        id=str(uuid.uuid4()),
        pool="default",
        action="validate",
        status=Status.pending,
        payload={"args": args},
    )


@validate_app.command("run")
def run(
    kind: str = typer.Argument(..., help=f"Artifact type ({', '.join(VALID_KINDS)})"),
    path: Optional[Path] = typer.Argument(None, exists=False, readable=True, resolve_path=True),
    json_out: bool = typer.Option(False, "--json"),
) -> None:
    if kind not in VALID_KINDS:
        typer.echo(f"Unknown kind '{kind}'. Choose from: {', '.join(VALID_KINDS)}", err=True)
        raise typer.Exit(1)

    args = {"kind": kind, "path": str(path) if path else None}
    task = _build_task(args)

    result = asyncio.run(validate_handler(json.loads(task.model_dump_json())))

    if json_out:
        typer.echo(json.dumps(result, indent=2))
    else:
        if result.get("ok"):
            typer.secho("✅  Valid", fg=typer.colors.GREEN)
        else:
            typer.secho("❌  Invalid", fg=typer.colors.RED, err=True)
            for msg in result.get("errors", []):
                typer.echo(f"   • {msg}", err=True)
            raise typer.Exit(1)


@validate_app.command("submit")
def submit(
    kind: str = typer.Argument(..., help=f"Artifact type ({', '.join(VALID_KINDS)})"),
    path: Optional[Path] = typer.Argument(None, exists=False, readable=True, resolve_path=True),
    gateway_url: str = typer.Option(
        DEFAULT_GATEWAY,
        "--gateway",
        envvar="PEAGEN_GATEWAY_URL",
        help="JSON-RPC gateway endpoint.",
    ),
) -> None:
    if kind not in VALID_KINDS:
        typer.echo(f"Unknown kind '{kind}'. Choose from: {', '.join(VALID_KINDS)}", err=True)
        raise typer.Exit(1)

    args = {"kind": kind, "path": str(path) if path else None}
    task = _build_task(args)

    rpc_req = {
        "jsonrpc": "2.0",
        "id": task.id,
        "method": "Task.submit",
        "params": {"task": task.model_dump()},
    }

    with httpx.Client(timeout=30.0) as client:
        resp = client.post(gateway_url, json=rpc_req)
        resp.raise_for_status()
        reply = resp.json()

    if "error" in reply:
        typer.secho(
            f"Remote error {reply['error']['code']}: {reply['error']['message']}",
            fg=typer.colors.RED,
            err=True,
        )
        raise typer.Exit(1)

    typer.secho(f"Submitted task {task.id}", fg=typer.colors.GREEN)
    if reply.get("result"):
        typer.echo(json.dumps(reply["result"], indent=2))
