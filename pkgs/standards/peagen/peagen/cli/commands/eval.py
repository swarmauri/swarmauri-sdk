# peagen/commands/eval.py
"""
CLI interface for program evaluation.

Sub-commands
------------
eval run     – local, blocking execution
eval submit  – JSON-RPC dispatch to worker farm
"""

from __future__ import annotations

import asyncio
import json
import time
from pathlib import Path
from typing import Optional, Dict, Any

import typer

from peagen.cli.task_helpers import build_task, submit_task, get_task
from peagen.handlers.eval_handler import eval_handler
from peagen.orm import Status
from peagen.defaults import DEFAULT_POOL_ID

# ────────────────────────── apps ───────────────────────────────

local_eval_app = typer.Typer(help="Evaluate programs locally.")
remote_eval_app = typer.Typer(help="Submit evaluations to the gateway.")


# ─────────── helper ---------------------------------------------------
def _common_args(
    program_glob: str,
    pool: Optional[str],
    async_eval: bool,
    strict: bool,
    skip_failed: bool,
) -> Dict[str, Any]:
    return {
        "program_glob": program_glob,
        "pool": pool,
        "async_eval": async_eval,
        "strict": strict,
        "skip_failed": skip_failed,
    }


# ───────────────────────── local run ───────────────────────────────────
@local_eval_app.command("eval")
def run(  # noqa: PLR0913
    ctx: typer.Context,
    program_glob: str = typer.Argument("**/*.*", help="Glob for program files"),
    pool: Optional[str] = typer.Option(None, "--pool", "-p"),
    async_eval: bool = typer.Option(False, "--async/--no-async"),
    strict: bool = typer.Option(False, "--strict"),
    skip_failed: bool = typer.Option(False, "--skip-failed/--include-failed"),
    json_out: bool = typer.Option(False, "--json"),
    out: Optional[Path] = typer.Option(None, "--out"),
    repo: str = typer.Option(..., "--repo", help="Git repo URI"),
    ref: str = typer.Option("HEAD", "--ref"),
) -> None:
    """Run program evaluation synchronously."""
    args = _common_args(program_glob, pool, async_eval, strict, skip_failed) | {
        "repo": repo,
        "ref": ref,
    }

    task = build_task(
        action="eval",
        args=args,
        pool_id=str(DEFAULT_POOL_ID),
        repo=repo,
        ref=ref,
    )

    result = asyncio.run(eval_handler(task))
    report = result["report"]

    # output
    if json_out:
        typer.echo(json.dumps(report, indent=2))
    else:
        out_file = (out or Path(".peagen")) / "eval_report.json"
        out_file.parent.mkdir(parents=True, exist_ok=True)
        out_file.write_text(json.dumps(report, indent=2))
        typer.echo(str(out_file))

    if result["strict_failed"]:
        raise typer.Exit(3)


# ───────────────────────── remote submit ───────────────────────────────
@remote_eval_app.command("eval")
def submit(  # noqa: PLR0913
    ctx: typer.Context,
    program_glob: str = typer.Argument("**/*.*"),
    pool: Optional[str] = typer.Option(None, "--pool", "-p"),
    async_eval: bool = typer.Option(False, "--async/--no-async"),
    strict: bool = typer.Option(False, "--strict"),
    skip_failed: bool = typer.Option(False, "--skip-failed/--include-failed"),
    repo: str = typer.Option(..., "--repo"),
    ref: str = typer.Option("HEAD", "--ref"),
    watch: bool = typer.Option(False, "--watch", "-w"),
    interval: float = typer.Option(2.0, "--interval", "-i"),
) -> None:
    """Enqueue evaluation on the gateway (optionally watch until done)."""
    args = _common_args(program_glob, pool, async_eval, strict, skip_failed) | {
        "repo": repo,
        "ref": ref,
    }

    task = build_task(
        action="eval",
        args=args,
        pool_id=str(DEFAULT_POOL_ID),
        repo=repo,
        ref=ref,
    )

    rpc = ctx.obj["rpc"]
    created = submit_task(rpc, task)
    typer.echo(f"Submitted task {created['id']}")

    if watch:
        while True:
            cur = get_task(rpc, created["id"])
            if Status.is_terminal(cur.status):
                break
            time.sleep(interval)
        typer.echo(json.dumps(cur.model_dump(), indent=2))
