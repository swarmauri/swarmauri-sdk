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
import time
from pathlib import Path
import tempfile
from typing import Any, Dict, Optional

import typer
from peagen._utils.config_loader import _effective_cfg, load_peagen_toml
from peagen.handlers.process_handler import process_handler
from peagen.transport import TASK_SUBMIT, TASK_GET
from peagen.transport.jsonrpc_schemas.task import GetParams, GetResult
from peagen.cli.rpc_utils import rpc_post
from peagen.transport.jsonrpc_schemas import Status
from peagen.cli.task_helpers import build_task, submit_task

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
    repo: str = typer.Option(..., "--repo", help="Git repository URI"),
    ref: str = typer.Option("HEAD", "--ref", help="Git ref or commit SHA"),
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
    if repo:
        args.update({"repo": repo, "ref": ref})
    task = build_task("process", args, pool=ctx.obj.get("pool", "default"))
    task.payload["cfg_override"] = cfg_override

    result = asyncio.run(process_handler(task))
    typer.echo(json.dumps(result, indent=2))


# ────────────────────────── remote submit ────────────────────────────────────
@remote_process_app.command("process")
def submit(  # noqa: PLR0913 – CLI signature needs many options
    ctx: typer.Context,
    projects_payload: str = typer.Argument(
        ..., help="Path to YAML file or inline text for PROJECTS"
    ),
    project_name: Optional[str] = typer.Option(
        None, help="Process only a single project by its NAME"
    ),
    start_idx: int = typer.Option(0, help="Index offset for rendered filenames"),
    start_file: Optional[str] = typer.Option(
        None, help="Skip files until this RENDERED_FILE_NAME is reached"
    ),
    transitive: bool = typer.Option(
        False, "--transitive/--no-transitive", help="Include transitive deps"
    ),
    agent_env: Optional[str] = typer.Option(
        None, help="JSON settings for the LLM agent environment"
    ),
    output_base: Optional[Path] = typer.Option(
        None, "--output-base", help="Root dir for materialised artifacts"
    ),
    repo: Optional[str] = typer.Option(None, "--repo", help="Git repository URI"),
    ref: str = typer.Option("HEAD", "--ref", help="Git ref or commit SHA"),
    watch: bool = typer.Option(False, "--watch", "-w", help="Poll until finished"),
    interval: float = typer.Option(
        2.0, "--interval", "-i", help="Seconds between polls"
    ),
):
    """Enqueue a processing task via JSON-RPC and return immediately."""
    # Pass a pointer to the YAML file rather than embedding the text
    path = Path(projects_payload)
    if path.is_file():
        payload_pointer = str(path.resolve())
    else:
        if path.suffix in {".yml", ".yaml"}:
            raise typer.BadParameter(f"File not found: {projects_payload}")
        tmp = Path(tempfile.mkdtemp(prefix="peagen_pp_")) / "projects_payload.yaml"
        tmp.write_text(projects_payload, encoding="utf-8")
        payload_pointer = str(tmp)

    args = _collect_args(
        payload_pointer,
        project_name,
        start_idx,
        start_file,
        transitive,
        agent_env,
        output_base,
    )
    if repo:
        args.update({"repo": repo, "ref": ref})
    task = build_task("process", args, pool=ctx.obj.get("pool", "default"))

    # ─────────────────────── cfg override  ──────────────────────────────
    inline = ctx.obj.get("task_override_inline")  # JSON string or None
    file_ = ctx.obj.get("task_override_file")  # Path or None
    cfg_override: Dict[str, Any] = {}
    if inline:
        cfg_override = json.loads(inline)
    if file_:
        cfg_override.update(load_peagen_toml(Path(file_), required=True))
    task.payload["cfg_override"] = cfg_override

    reply = submit_task(ctx.obj.get("gateway_url"), task)
    data = reply

    tid = task.id
    typer.secho(f"Submitted task {tid}", fg=typer.colors.GREEN)
    if data.get("result") is not None:
        typer.echo(json.dumps(data["result"], indent=2))
    if watch:

        def _rpc_call() -> GetResult:
            res = rpc_post(
                ctx.obj.get("gateway_url"),
                TASK_GET,
                GetParams(taskId=tid).model_dump(),
                result_model=GetResult,
            )
            return res.result  # type: ignore[return-value]

        while True:
            task_reply = _rpc_call()
            typer.echo(json.dumps(task_reply.model_dump(), indent=2))
            if Status.is_terminal(task_reply.status):
                break
            time.sleep(interval)
