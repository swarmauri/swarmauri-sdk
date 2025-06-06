# peagen/commands/process.py
"""
CLI front-end for the processing pipeline.

Two sub-commands are exposed:

  • ``peagen process run``     – local, blocking execution
  • ``peagen process submit``  – JSON-RPC submission to worker farm
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any, Dict, Optional

import httpx
import typer

from peagen.handlers.process_handler import process_handler
from peagen.models import Status, Task  # noqa: F401 – only for type hints

DEFAULT_GATEWAY = "http://localhost:8000/rpc"
local_process_app = typer.Typer(help="Render / generate project files.")
remote_process_app = typer.Typer(help="Render / generate project files.")


# ────────────────────────── helpers ──────────────────────────────────────────
def _collect_args(  # noqa: C901 – straight-through mapper
    projects_payload: str,
    project_name: Optional[str],
    start_idx: int,
    start_file: Optional[str],
    verbose: int,
    transitive: bool,
    agent_env: Optional[str],
    output_base: Optional[Path],
) -> Dict[str, Any]:
    args: Dict[str, Any] = {
        "projects_payload": projects_payload,
        "project_name": project_name,
        "start_idx": start_idx,
        "start_file": start_file,
        "verbose": verbose,
        "transitive": transitive,
        "output_base": str(output_base) if output_base else None,
    }
    if agent_env:
        try:
            args["agent_env"] = json.loads(agent_env)
        except json.JSONDecodeError as exc:
            raise typer.BadParameter("--agent-env must be valid JSON") from exc
    return args


def _build_task(args: Dict[str, Any]) -> Task:
    """Fabricate a Task model so the CLI uses the same payload shape as workers."""
    return Task(
        pool="default",
        payload={"action": "process", "args": args},
    )


# ────────────────────────── local run ────────────────────────────────────────
@local_process_app.command("process")
def run(  # noqa: PLR0913 – CLI signature needs many options
    ctx: typer.Context,
    projects_payload: str = typer.Argument(
        ..., help="Path to YAML file containing a top-level PROJECTS list."
    ),
    project_name: Optional[str] = typer.Option(
        None, help="Process only a single project by its NAME."
    ),
    start_idx: int = typer.Option(
        0, "--start-idx", help="Index offset for rendered filenames."
    ),
    start_file: Optional[str] = typer.Option(
        None, help="Skip files until this RENDERED_FILE_NAME is reached."
    ),
    verbose: int = typer.Option(
        0, "--verbose", "-v", count=True, help="Increase log verbosity."
    ),
    transitive: bool = typer.Option(
        False, "--transitive/--no-transitive", help="Include transitive deps."
    ),
    agent_env: Optional[str] = typer.Option(
        None,
        help=(
            "JSON for LLM driver, e.g. "
            '\'{"provider":"openai","model_name":"gpt-4o","api_key":"sk-..."}\''
        ),
    ),
    output_base: Optional[Path] = typer.Option(
        None,
        "--output-base",
        help="Root dir for materialised artifacts (default ./out).",
    ),
):
    """Execute the processing pipeline synchronously on this machine."""
    args = _collect_args(
        projects_payload,
        project_name,
        start_idx,
        start_file,
        verbose,
        transitive,
        agent_env,
        output_base,
    )
    task = _build_task(args)

    result = asyncio.run(process_handler(task))
    typer.echo(json.dumps(result, indent=2))


# ────────────────────────── remote submit ────────────────────────────────────
@remote_process_app.command("process")
def submit(  # noqa: PLR0913 – CLI signature needs many options
    ctx: typer.Context,
    projects_payload: str = typer.Argument(...),
    project_name: Optional[str] = typer.Option(None),
    start_idx: int = typer.Option(0),
    start_file: Optional[str] = typer.Option(None),
    verbose: int = typer.Option(0, "--verbose", "-v", count=True),
    transitive: bool = typer.Option(False, "--transitive/--no-transitive"),
    agent_env: Optional[str] = typer.Option(None),
    output_base: Optional[Path] = typer.Option(None, "--output-base"),
):
    """Enqueue a processing task via JSON-RPC and return immediately."""
    args = _collect_args(
        projects_payload,
        project_name,
        start_idx,
        start_file,
        verbose,
        transitive,
        agent_env,
        output_base,
    )
    task = _build_task(args)

    rpc_req = {
        "jsonrpc": "2.0",
        "method": "Task.submit",
        "params": {"pool": task.pool, "payload": task.payload, "taskId": task.id},
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
        raise typer.Exit(code=1)

    typer.secho(f"Submitted task {task.id}", fg=typer.colors.GREEN)
    if reply.get("result"):
        typer.echo(json.dumps(reply["result"], indent=2))
