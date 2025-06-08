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
import yaml
from peagen._utils.config_loader import _effective_cfg, load_peagen_toml
from peagen.handlers.process_handler import process_handler
from peagen.models import Status, Task  # noqa: F401 – only for type hints

local_process_app = typer.Typer(help="Render / generate project files.")
remote_process_app = typer.Typer(help="Render / generate project files.")


# ────────────────────────── helpers ──────────────────────────────────────────
def _collect_args(  # noqa: C901 – straight-through mapper
    projects_payload: Any,
    project_name: Optional[str],
    start_idx: int,
    start_file: Optional[str],
    transitive: bool,
    agent_env: Optional[str],
    output_base: Optional[Path],
) -> Dict[str, Any]:
    """Package CLI options into a payload dictionary.

    ``projects_payload`` may be a path, YAML text or a pre-parsed mapping. The
    remote submission command converts YAML to a Python object so workers don't
    need to read local files.
    """
    args: Dict[str, Any] = {
        "projects_payload": projects_payload,
        "project_name": project_name,
        "start_idx": start_idx,
        "start_file": start_file,
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
    cfg_path: Optional[Path] = ctx.obj.get("config_path") if ctx.obj else None
    cfg_override = _effective_cfg(cfg_path)

    args = _collect_args(
        projects_payload,
        project_name,
        start_idx,
        start_file,
        transitive,
        agent_env,
        output_base,
    )
    task = _build_task(args)
    task.payload["cfg_override"] = cfg_override

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
    transitive: bool = typer.Option(False, "--transitive/--no-transitive"),
    agent_env: Optional[str] = typer.Option(None),
    output_base: Optional[Path] = typer.Option(None, "--output-base"),
):
    """Enqueue a processing task via JSON-RPC and return immediately."""
    # Parse the YAML locally and send the resulting dict to remote workers
    path = Path(projects_payload)
    if path.is_file():
        yaml_text = path.read_text(encoding="utf-8")
    else:
        if path.suffix in {".yml", ".yaml"}:
            raise typer.BadParameter(f"File not found: {projects_payload}")
        yaml_text = projects_payload

    yaml_data = yaml.safe_load(yaml_text)

    args = _collect_args(
        yaml_data,
        project_name,
        start_idx,
        start_file,
        transitive,
        agent_env,
        output_base,
    )
    task = _build_task(args)

    # ─────────────────────── cfg override  ──────────────────────────────
    inline = ctx.obj.get("task_override_inline")  # JSON string or None
    file_ = ctx.obj.get("task_override_file")  # Path or None
    cfg_override: Dict[str, Any] = {}
    if inline:
        cfg_override = json.loads(inline)
    if file_:
        cfg_override.update(load_peagen_toml(Path(file_), required=True))
    task.payload["cfg_override"] = cfg_override

    rpc_req = {
        "jsonrpc": "2.0",
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
        raise typer.Exit(code=1)

    typer.secho(f"Submitted task {task.id}", fg=typer.colors.GREEN)
    if reply.get("result"):
        typer.echo(json.dumps(reply["result"], indent=2))
