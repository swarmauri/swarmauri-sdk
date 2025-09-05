# peagen/cli/commands/mutate.py
"""
CLI for the *mutate* workflow.

Sub-commands
------------
• peagen mutate run       – local, blocking execution
• peagen mutate submit    – enqueue via gateway
"""

from __future__ import annotations

import asyncio
import json
import time
from pathlib import Path
from typing import Optional, Dict, Any

import typer

from peagen.handlers.mutate_handler import mutate_handler
from peagen.cli.task_helpers import build_task, submit_task, get_task
from peagen.orm import Status
from peagen.defaults import DEFAULT_POOL_ID

# ────────────────────────── apps ───────────────────────────────


local_mutate_app = typer.Typer(help="Run mutate workflow locally.")
remote_mutate_app = typer.Typer(help="Submit mutate workflow to gateway.")


# ───────────────────── helper to assemble args ────────────────────────
def _args_dict(
    target_file: str,
    import_path: str,
    entry_fn: str,
    profile_mod: Optional[str],
    fitness: str,
    mutator: str,
    gens: int,
) -> Dict[str, Any]:
    return {
        "target_file": target_file,
        "import_path": import_path,
        "entry_fn": entry_fn,
        "profile_mod": profile_mod,
        "gens": gens,
        "evaluator_ref": fitness,
        "mutations": [{"kind": mutator}],
    }


# ─────────────────────── LOCAL RUN ────────────────────────────────────
@local_mutate_app.command("mutate")
def run(  # noqa: PLR0913
    ctx: typer.Context,
    target_file: str,
    import_path: str,
    entry_fn: str,
    profile_mod: Optional[str] = None,
    fitness: str = typer.Option(
        "peagen.plugins.evaluators.performance_evaluator:PerformanceEvaluator",
        "--fitness",
    ),
    mutator: str = typer.Option("default_mutator", "--mutator"),
    gens: int = typer.Option(1, "--gens"),
    json_out: bool = typer.Option(False, "--json"),
    out: Optional[Path] = typer.Option(None, "--out"),
    repo: str = typer.Option(..., "--repo"),
    ref: str = typer.Option("HEAD", "--ref"),
) -> None:
    """Run the mutate workflow synchronously on this machine."""
    args = _args_dict(
        target_file, import_path, entry_fn, profile_mod, fitness, mutator, gens
    ) | {"repo": repo, "ref": ref}

    task = build_task(
        action="mutate",
        args=args,
        pool_id=str(DEFAULT_POOL_ID),
        repo=repo,
        ref=ref,
    )

    result = asyncio.run(mutate_handler(task))

    if json_out:
        typer.echo(json.dumps(result, indent=2))
    else:
        outfile = out or Path(".") / "mutate_result.json"
        outfile.write_text(json.dumps(result, indent=2))
        typer.echo(str(outfile))


# ─────────────────────── REMOTE SUBMIT ─────────────────────────────────
@remote_mutate_app.command("mutate")
def submit(  # noqa: PLR0913
    ctx: typer.Context,
    target_file: str,
    import_path: str,
    entry_fn: str,
    profile_mod: Optional[str] = None,
    fitness: str = typer.Option(
        "peagen.plugins.evaluators.performance_evaluator:PerformanceEvaluator",
        "--fitness",
    ),
    mutator: str = typer.Option("default_mutator", "--mutator"),
    gens: int = typer.Option(1, "--gens"),
    repo: str = typer.Option(..., "--repo"),
    ref: str = typer.Option("HEAD", "--ref"),
    watch: bool = typer.Option(False, "--watch", "-w"),
    interval: float = typer.Option(2.0, "--interval", "-i"),
) -> None:
    """Submit a mutate task to the gateway (optionally watch progress)."""
    args = _args_dict(
        target_file, import_path, entry_fn, profile_mod, fitness, mutator, gens
    ) | {"repo": repo, "ref": ref}

    task = build_task(
        action="mutate",
        args=args,
        pool_id=str(DEFAULT_POOL_ID),
        repo=repo,
        ref=ref,
    )

    created = submit_task(ctx.obj["rpc"], task)
    typer.echo(f"Submitted task {created['id']}")

    if watch:
        while True:
            cur = get_task(ctx.obj["rpc"], created["id"])
            if Status.is_terminal(cur.status):
                break
            time.sleep(interval)
        typer.echo(json.dumps(cur.model_dump(), indent=2))
