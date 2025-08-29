"""
peagen.commands.evolve
──────────────────────
CLI wrapper for the Evolve workflow.

Sub-commands
------------
• peagen evolve run       – local expansion + mutate
• peagen evolve submit    – enqueue on the gateway (optional watch)
"""

from __future__ import annotations

import asyncio
import json
import time
from pathlib import Path
from typing import Optional, Dict, Any

import typer

from peagen.cli.task_helpers import build_task, submit_task, get_task
from peagen.handlers.evolve_handler import evolve_handler
from peagen.core.validate_core import validate_evolve_spec
from peagen.orm import Status, Action

from peagen.defaults import DEFAULT_POOL_ID

# ────────────────────────── apps ───────────────────────────────

local_evolve_app = typer.Typer(help="Expand & mutate evolve spec locally.")
remote_evolve_app = typer.Typer(help="Submit evolve spec to the gateway.")


# ---------------------------------------------------------------------
def _args_for_task(spec: Path, repo: str, ref: str) -> Dict[str, Any]:
    return {
        "evolve_spec": str(spec),
        "repo": repo,
        "ref": ref,
    }


# ─────────────────────────── LOCAL RUN ────────────────────────────────
@local_evolve_app.command("evolve")
def run(
    ctx: typer.Context,
    spec: Path = typer.Argument(..., exists=True, help="Evolve spec YAML"),
    json_out: bool = typer.Option(False, "--json"),
    out: Optional[Path] = typer.Option(None, "--out", help="Write result file"),
    repo: str = typer.Option(..., "--repo", help="Git repository URI"),
    ref: str = typer.Option("HEAD", "--ref"),
) -> None:
    """Validate + expand evolve spec on the local machine."""
    val = validate_evolve_spec(spec)
    if not val["ok"]:
        for err in val["errors"]:
            typer.secho(err, fg=typer.colors.RED, err=True)
        raise typer.Exit(1)

    task = build_task(
        action=Action.EVOLVE,
        args=_args_for_task(spec, repo, ref),
        pool_id=str(DEFAULT_POOL_ID),
        repo=repo,
        ref=ref,
    )

    result = asyncio.run(evolve_handler(task))

    if json_out:
        typer.echo(json.dumps(result, indent=2))
    else:
        outfile = out or spec.with_suffix(".evolve_result.json")
        outfile.write_text(json.dumps(result, indent=2))
        typer.echo(str(outfile))


# ───────────────────────── REMOTE SUBMIT ──────────────────────────────
@remote_evolve_app.command("evolve")
def submit(
    ctx: typer.Context,
    spec: Path = typer.Argument(..., exists=True, help="Evolve spec YAML"),
    watch: bool = typer.Option(False, "--watch", "-w"),
    interval: float = typer.Option(2.0, "--interval", "-i"),
    repo: str = typer.Option(..., "--repo"),
    ref: str = typer.Option("HEAD", "--ref"),
) -> None:
    """Submit evolve spec to the gateway; optionally watch until done."""
    val = validate_evolve_spec(spec)
    if not val["ok"]:
        for err in val["errors"]:
            typer.secho(err, fg=typer.colors.RED, err=True)
        raise typer.Exit(1)

    task = build_task(
        action=Action.EVOLVE,
        args=_args_for_task(spec, repo, ref),
        pool_id=str(DEFAULT_POOL_ID),
        repo=repo,
        ref=ref,
    )

    rpc = ctx.obj["rpc"]

    created = submit_task(rpc, task)
    typer.secho(f"Submitted task {created['id']}", fg=typer.colors.GREEN)

    if watch:
        while True:
            cur = get_task(rpc, created["id"])
            if Status.is_terminal(cur.status):
                break
            time.sleep(interval)
        typer.echo(json.dumps(cur.model_dump(), indent=2))
