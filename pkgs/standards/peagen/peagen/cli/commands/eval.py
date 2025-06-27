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
import uuid
from pathlib import Path
from typing import Any, Dict, Optional

import httpx
import typer
from peagen._utils.config_loader import load_peagen_toml

from peagen.handlers.eval_handler import eval_handler
from peagen.orm import Status, Task

DEFAULT_GATEWAY = "http://localhost:8000/rpc"
local_eval_app = typer.Typer(
    help="Evaluate workspace programs against an EvaluatorPool."
)
remote_eval_app = typer.Typer(
    help="Evaluate workspace programs against an EvaluatorPool."
)


# ───────────────────────── helpers ─────────────────────────────────────────
def _build_task(args: dict, pool: str) -> Task:
    return Task(
        id=str(uuid.uuid4()),
        pool=pool,
        status=Status.waiting,
        payload={"action": "eval", "args": args},
    )


# ───────────────────────── local run ───────────────────────────────────────
@local_eval_app.command("eval")
def run(  # noqa: PLR0913 – CLI needs many options
    ctx: typer.Context,
    workspace_uri: str = typer.Argument(..., help="Workspace path or URI"),
    program_glob: str = typer.Argument("**/*.*", help="Glob pattern for programs"),
    pool: Optional[str] = typer.Option(None, "--pool", "-p", help="EvaluatorPool ref"),
    async_eval: bool = typer.Option(False, "--async/--no-async"),
    strict: bool = typer.Option(False, "--strict"),
    skip_failed: bool = typer.Option(False, "--skip-failed/--include-failed"),
    json_out: bool = typer.Option(False, "--json"),
    out: Optional[Path] = typer.Option(None, "--out"),
    repo: Optional[str] = typer.Option(None, "--repo", help="Git repository URI"),
    ref: str = typer.Option("HEAD", "--ref", help="Git ref or commit SHA"),
):
    """Run evaluation synchronously on this machine."""
    args = {
        "workspace_uri": workspace_uri if not repo else f"git+{repo}@{ref}",
        "program_glob": program_glob,
        "pool": pool,
        "async_eval": async_eval,
        "strict": strict,
        "skip_failed": skip_failed,
    }
    if repo:
        args.update({"repo": repo, "ref": ref})
    task = _build_task(args, ctx.obj.get("pool", "default"))
    result = asyncio.run(eval_handler(task))
    report = result["report"]

    # ----- output ----------------------------------------------------------
    if json_out:
        typer.echo(json.dumps(report, indent=2))
    else:
        out_dir = out or Path(workspace_uri) / ".peagen"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_file = out_dir / "eval_report.json"
        out_file.write_text(json.dumps(report, indent=2))
        typer.echo(str(out_file))

    # ----- strict gate -----------------------------------------------------
    if result["strict_failed"]:
        raise typer.Exit(3)


# ───────────────────────── remote submit ───────────────────────────────────
@remote_eval_app.command("eval")
def submit(  # noqa: PLR0913
    ctx: typer.Context,
    workspace_uri: str = typer.Argument(..., help="Workspace path or URI"),
    program_glob: str = typer.Argument("**/*.*", help="Glob pattern for program files"),
    pool: Optional[str] = typer.Option(
        None, "--pool", "-p", help="EvaluatorPool reference"
    ),
    async_eval: bool = typer.Option(
        False, "--async/--no-async", help="Run evaluations asynchronously"
    ),
    strict: bool = typer.Option(
        False, "--strict", help="Fail if any program exit code is non-zero"
    ),
    skip_failed: bool = typer.Option(
        False, "--skip-failed/--include-failed", help="Ignore failed programs"
    ),
    repo: Optional[str] = typer.Option(None, "--repo", help="Git repository URI"),
    ref: str = typer.Option("HEAD", "--ref", help="Git ref or commit SHA"),
):
    """Enqueue evaluation on a remote worker."""
    args = {
        "workspace_uri": workspace_uri if not repo else f"git+{repo}@{ref}",
        "program_glob": program_glob,
        "pool": pool,
        "async_eval": async_eval,
        "strict": strict,
        "skip_failed": skip_failed,
    }
    task = _build_task(args, ctx.obj.get("pool", "default"))

    # ─────────────────────── cfg override  ──────────────────────────────
    inline = ctx.obj.get("task_override_inline")
    file_ = ctx.obj.get("task_override_file")
    cfg_override: Dict[str, Any] = {}
    if inline:
        cfg_override = json.loads(inline)
    if file_:
        cfg_override.update(load_peagen_toml(Path(file_), required=True))
    task.payload["cfg_override"] = cfg_override

    rpc_req = {
        "jsonrpc": "2.0",
        "id": task.id,
        "method": "Task.submit",
        "params": {"taskId": task.id, "pool": task.pool, "payload": task.payload},
    }

    with httpx.Client(timeout=30.0) as client:
        resp = client.post(ctx.obj.get("gateway_url"), json=rpc_req)
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
