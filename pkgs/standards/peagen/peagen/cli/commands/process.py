# peagen/commands/process.py
"""
CLI front-end for the “process” pipeline.

Sub-commands
------------
• peagen process run     – local, blocking execution
• peagen process submit  – JSON-RPC submission to the gateway
"""

from __future__ import annotations

import asyncio
import json
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, Optional

import typer

from peagen._utils.config_loader import _effective_cfg, load_peagen_toml
from peagen.cli.task_helpers import build_task, submit_task, get_task
from peagen.handlers.process_handler import process_handler
from peagen.orm import Status

from peagen.defaults import DEFAULT_POOL_ID

# ────────────────────────── apps ───────────────────────────────

local_process_app = typer.Typer(help="Render / generate project files locally.")
remote_process_app = typer.Typer(help="Submit processing tasks to the gateway.")


# ────────────────────────── helpers ──────────────────────────────────
def _collect_args(  # noqa: C901 – param mapper
    projects_payload: str,
    project_name: Optional[str],
    start_idx: int,
    start_file: Optional[str],
    transitive: bool,
    agent_env: Optional[str],
    output_base: Optional[Path],
) -> Dict[str, Any]:
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


def _determine_pool_id(ctx: typer.Context) -> str:
    """Return pool_id to embed in TaskCreate."""
    return str(ctx.obj.get("pool_id", DEFAULT_POOL_ID))


# ────────────────────────── LOCAL RUN ────────────────────────────────
@local_process_app.command("process")
def run(  # noqa: PLR0913
    ctx: typer.Context,
    projects_payload: str = typer.Argument(..., help="Path to PROJECTS YAML"),
    project_name: Optional[str] = typer.Option(None, "--project-name"),
    start_idx: int = typer.Option(0, "--start-idx"),
    start_file: Optional[str] = typer.Option(None, "--start-file"),
    transitive: bool = typer.Option(False, "--transitive/--no-transitive"),
    agent_env: Optional[str] = typer.Option(None, "--agent-env"),
    output_base: Optional[Path] = typer.Option(None, "--output-base"),
    repo: str = typer.Option(..., "--repo"),
    ref: str = typer.Option("HEAD", "--ref"),
) -> None:
    """Run the processing pipeline locally."""
    cfg_override = _effective_cfg(ctx.obj.get("config_path"))
    args = _collect_args(
        projects_payload,
        project_name,
        start_idx,
        start_file,
        transitive,
        agent_env,
        output_base,
    ) | {"repo": repo, "ref": ref, "cfg_override": cfg_override}

    task = build_task(
        action="process",
        args=args,
        pool_id=_determine_pool_id(ctx),
        repo=repo,
        ref=ref,
    )

    result = asyncio.run(process_handler(task))
    typer.echo(json.dumps(result, indent=2))


# ────────────────────────── REMOTE SUBMIT ────────────────────────────
@remote_process_app.command("process")
def submit(  # noqa: PLR0913
    ctx: typer.Context,
    projects_payload: str = typer.Argument(
        ..., help="Path to YAML file or inline text"
    ),
    project_name: Optional[str] = typer.Option(None, "--project-name"),
    start_idx: int = typer.Option(0, "--start-idx"),
    start_file: Optional[str] = typer.Option(None, "--start-file"),
    transitive: bool = typer.Option(False, "--transitive/--no-transitive"),
    agent_env: Optional[str] = typer.Option(None, "--agent-env"),
    output_base: Optional[Path] = typer.Option(None, "--output-base"),
    repo: str = typer.Option(..., "--repo"),
    ref: str = typer.Option("HEAD", "--ref"),
    watch: bool = typer.Option(False, "--watch", "-w"),
    interval: float = typer.Option(2.0, "--interval", "-i"),
) -> None:
    """Submit a processing task via JSON-RPC."""
    # If inline YAML provided, write to temp file so worker can fetch.
    payload_path = Path(projects_payload)
    if not payload_path.is_file():
        if payload_path.suffix in {".yml", ".yaml"}:
            raise typer.BadParameter(f"File not found: {projects_payload}")
        tmp_dir = Path(tempfile.mkdtemp(prefix="peagen_pp_"))
        payload_path = tmp_dir / "projects_payload.yaml"
        payload_path.write_text(projects_payload, encoding="utf-8")

    args = _collect_args(
        str(payload_path),
        project_name,
        start_idx,
        start_file,
        transitive,
        agent_env,
        output_base,
    ) | {"repo": repo, "ref": ref}

    # cfg overrides – inline JSON / TOML file
    cfg_override: Dict[str, Any] = {}
    if inline := ctx.obj.get("task_override_inline"):
        cfg_override = json.loads(inline)
    if file_ := ctx.obj.get("task_override_file"):
        cfg_override.update(load_peagen_toml(Path(file_), required=True))
    if cfg_override:
        args["cfg_override"] = cfg_override

    task = build_task(
        action="process",
        args=args,
        pool_id=_determine_pool_id(ctx),
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
