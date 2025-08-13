"""
peagen.cli.commands.doe
────────────────────────────────────────
CLI wrapper for Design-of-Experiments (DOE) utilities.

• `peagen doe gen`       – local expansion
• `peagen doe process`   – local processing
• `peagen remote-doe …`  – submit tasks to the gateway
"""

from __future__ import annotations

import asyncio
import json
import time
from pathlib import Path
from typing import Optional, Dict, Any

import typer

from peagen.cli.task_helpers import (
    build_task,
    submit_task,
    get_task,
)
from peagen.handlers.doe_handler import doe_handler
from peagen.handlers.doe_process_handler import doe_process_handler
from peagen.orm import Status
from peagen.defaults import DEFAULT_POOL_ID

# ────────────────────────── apps ───────────────────────────────


local_doe_app = typer.Typer(help="Generate project-payload bundles locally.")
remote_doe_app = typer.Typer(help="Submit DOE jobs to the gateway.")


# ───────────────────────── helper util ───────────────────────────
def _assemble_args(
    spec: Path,
    template: Path,
    output: Path,
    *,
    config: Optional[Path],
    dry_run: bool = False,
    force: bool = False,
    skip_validate: bool = False,
    evaluate_runs: bool = False,
) -> Dict[str, Any]:
    return {
        "spec": str(spec),
        "template": str(template),
        "output": str(output),
        "config": str(config) if config else None,
        "dry_run": dry_run,
        "force": force,
        "skip_validate": skip_validate,
        "evaluate_runs": evaluate_runs,
    }


# ───────────────────────────── local run ──────────────────────────────
@local_doe_app.command("gen")
def run_gen(  # noqa: PLR0913
    ctx: typer.Context,
    spec: Path,
    template: Path,
    output: Path = Path("project_payloads.yaml"),
    config: Optional[Path] = typer.Option(None, "-c", "--config"),
    dry_run: bool = typer.Option(False, "--dry-run"),
    force: bool = typer.Option(False, "--force"),
    skip_validate: bool = typer.Option(False, "--skip-validate"),
    json_out: bool = typer.Option(False, "--json"),
    evaluate_runs: bool = typer.Option(False, "--eval-runs"),
    repo: str = typer.Option(..., "--repo"),
    ref: str = typer.Option("HEAD", "--ref"),
) -> None:
    """Generate a project-payload bundle locally."""
    args = _assemble_args(
        spec,
        template,
        output,
        config=config,
        dry_run=dry_run,
        force=force,
        skip_validate=skip_validate,
        evaluate_runs=evaluate_runs,
    ) | {"repo": repo, "ref": ref}

    task = build_task(
        action="doe",
        args=args,
        pool_id=str(DEFAULT_POOL_ID),
        repo=repo,
        ref=ref,
    )
    result = asyncio.run(doe_handler(task))
    typer.echo(
        json.dumps(result, indent=2)
        if json_out
        else f"✅ {', '.join(result.get('outputs', []))}"
    )


# ───────────────────────── remote submit (gen) ─────────────────────────
@remote_doe_app.command("gen")
def submit_gen(  # noqa: PLR0913
    ctx: typer.Context,
    spec: Path,
    template: Path,
    output: Path = Path("project_payloads.yaml"),
    config: Optional[Path] = typer.Option(None, "-c", "--config"),
    force: bool = typer.Option(False, "--force"),
    skip_validate: bool = typer.Option(False, "--skip-validate"),
    evaluate_runs: bool = typer.Option(False, "--eval-runs"),
    repo: str = typer.Option(..., "--repo"),
    ref: str = typer.Option("HEAD", "--ref"),
) -> None:
    """Submit a DOE generation task to the gateway."""
    rpc = ctx.obj["rpc"]

    args = _assemble_args(
        spec,
        template,
        output,
        config=config,
        force=force,
        skip_validate=skip_validate,
        evaluate_runs=evaluate_runs,
    ) | {"repo": repo, "ref": ref}

    task = build_task(
        action="doe",
        args=args,
        pool_id=str(DEFAULT_POOL_ID),
        repo=repo,
        ref=ref,
    )

    reply = submit_task(rpc, task)
    typer.echo(f"Submitted task {reply['id']} (status={reply['status']})")


# ───────────────────────────── local process ──────────────────────────
@local_doe_app.command("process")
def run_process(  # noqa: PLR0913
    ctx: typer.Context,
    spec: Path,
    template: Path,
    output: Path = Path("project_payloads.yaml"),
    config: Optional[Path] = typer.Option(None, "-c", "--config"),
    dry_run: bool = typer.Option(False, "--dry-run"),
    force: bool = typer.Option(False, "--force"),
    skip_validate: bool = typer.Option(False, "--skip-validate"),
    json_out: bool = typer.Option(False, "--json"),
    evaluate_runs: bool = typer.Option(False, "--eval-runs"),
    repo: Optional[str] = typer.Option(None, "--repo"),
    ref: str = typer.Option("HEAD", "--ref"),
) -> None:
    """Process DOE specification locally."""
    args = _assemble_args(
        spec,
        template,
        output,
        config=config,
        dry_run=dry_run,
        force=force,
        skip_validate=skip_validate,
        evaluate_runs=evaluate_runs,
    )
    if repo:
        args |= {"repo": repo, "ref": ref}

    task = build_task(
        action="doe_process",
        args=args,
        pool_id=str(DEFAULT_POOL_ID),
        repo=repo,
        ref=ref,
    )
    result = asyncio.run(doe_process_handler(task))
    typer.echo(
        json.dumps(result, indent=2) if json_out else json.dumps(result, indent=2)
    )


# ───────────────────────── remote submit (process) ────────────────────
@remote_doe_app.command("process")
def submit_process(  # noqa: PLR0913
    ctx: typer.Context,
    spec: Path,
    template: Path,
    output: Path = Path("project_payloads.yaml"),
    config: Optional[Path] = typer.Option(None, "-c", "--config"),
    force: bool = typer.Option(False, "--force"),
    skip_validate: bool = typer.Option(False, "--skip-validate"),
    evaluate_runs: bool = typer.Option(False, "--eval-runs"),
    watch: bool = typer.Option(False, "--watch", "-w"),
    interval: float = typer.Option(2.0, "--interval", "-i"),
    repo: Optional[str] = typer.Option(None, "--repo"),
    ref: str = typer.Option("HEAD", "--ref"),
) -> None:
    """Submit DOE processing to the gateway and optionally watch progress."""
    rpc = ctx.obj["rpc"]

    def _rel(p: Path) -> str:
        try:
            return str(p.relative_to(Path.cwd()))
        except ValueError:
            return str(p)

    args = _assemble_args(
        _rel(spec),
        _rel(template),
        output,
        config=config,
        force=force,
        skip_validate=skip_validate,
        evaluate_runs=evaluate_runs,
    )
    if repo:
        args |= {"repo": repo, "ref": ref}

    task = build_task(
        action="doe_process",
        args=args,
        pool_id=str(DEFAULT_POOL_ID),
        repo=repo,
        ref=ref,
    )

    created = submit_task(rpc, task)
    typer.echo(f"Submitted task {created['id']}")

    if watch:
        while True:
            cur = get_task(rpc, created["id"])
            if Status.is_terminal(cur.status):
                break
            time.sleep(interval)
        typer.echo(json.dumps(cur.model_dump(), indent=2))
