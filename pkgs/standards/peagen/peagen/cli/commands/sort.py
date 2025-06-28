# peagen/commands/sort.py

import asyncio
import json
from pathlib import Path
from typing import Any, Dict, Optional

import typer

from peagen._utils.config_loader import _effective_cfg, load_peagen_toml
from peagen.handlers.sort_handler import sort_handler
from peagen.protocols import TASK_SUBMIT
from peagen.cli.rpc_utils import rpc_post

local_sort_app = typer.Typer(help="Sort generated project files.")
remote_sort_app = typer.Typer(help="Sort generated project files via JSON-RPC.")


@local_sort_app.command("sort")
def run_sort(  # ← now receives the Typer context
    ctx: typer.Context,
    projects_payload: str = typer.Argument(..., help="Path to the projects YAML file."),
    project_name: str = typer.Option(None, help="Name of the project to process."),
    start_idx: int = typer.Option(0, help="Index to start sorting from."),
    start_file: str = typer.Option(None, help="File to start sorting from."),
    transitive: bool = typer.Option(False, help="Include transitive dependencies."),
    show_dependencies: bool = typer.Option(False, help="Show dependency info."),
    repo: str = typer.Option(..., "--repo", help="Git repository URI"),
    ref: str = typer.Option("HEAD", "--ref", help="Git ref or commit SHA"),
):
    """
    Run sort **locally** (no queue).  We:

    1.  Build the effective configuration chosen by the top-level `--config/-c`
        flag (stored by `_global_ctx` in `ctx.obj["config_path"]`
    2.  Inject that config under ``cfg_override`` so the handler receives it.
    3.  Invoke the same ``sort_handler`` a worker uses.
    """
    # ─────────────────────── 1) config resolution ───────────────────────
    cfg_path: Optional[Path] = ctx.obj.get("config_path") if ctx.obj else None
    cfg_override = _effective_cfg(cfg_path)

    # ─────────────────────── 2) build Task model ────────────────────────
    args: Dict[str, Any] = {
        "projects_payload": projects_payload,
        "project_name": project_name,
        "start_idx": start_idx,
        "start_file": start_file,
        "transitive": transitive,
        "show_dependencies": show_dependencies,
    }
    if repo:
        args.update({"repo": repo, "ref": ref})
    task = {
        "pool": "default",
        "payload": {
            "action": "sort",
            "args": args,
            "cfg_override": cfg_override,
        },
    }

    # ─────────────────────── 3) call handler ────────────────────────────
    try:
        result: Dict[str, Any] = asyncio.run(sort_handler(task))
    except Exception as exc:
        typer.echo(f"[ERROR] Exception inside sort_handler: {exc}")
        raise typer.Exit(1)

    # ─────────────────────── 4) present output ──────────────────────────
    if "error" in result:
        typer.echo(f"[ERROR] {result['error']}")
        raise typer.Exit(1)

    if "sorted" in result:  # single-project mode
        for line in result["sorted"]:
            typer.echo(line)
    else:  # all-projects mode
        for proj, files in result.get("sorted_all_projects", {}).items():
            typer.echo(f"Project {proj}:")
            for line in files:
                typer.echo(f"  {line}")


@remote_sort_app.command("sort")
def submit_sort(
    ctx: typer.Context,
    projects_payload: str = typer.Argument(..., help="Path to the projects YAML file."),
    project_name: str = typer.Option(None, help="Name of the project to process."),
    start_idx: int = typer.Option(0, help="Index to start sorting from."),
    start_file: str = typer.Option(None, help="File to start sorting from."),
    transitive: bool = typer.Option(False, help="Include transitive dependencies."),
    show_dependencies: bool = typer.Option(False, help="Show dependency info."),
    repo: str = typer.Option(..., "--repo", help="Git repository URI"),
    ref: str = typer.Option("HEAD", "--ref", help="Git ref or commit SHA"),
):
    """
    Submit this sort as a background task. Returns immediately with a taskId.
    """
    # 1) Create a Task instance
    # 1a) replace path with YAML text -------------------------------
    with open(projects_payload, "rt", encoding="utf-8") as fh:
        yaml_text = fh.read()

    # ─────────────────────── 1b) cfg override  ──────────────────────────
    inline = ctx.obj.get("task_override_inline")  # JSON or None
    file_ = ctx.obj.get("task_override_file")  # Path or None

    cfg_override: dict = {}
    if inline:
        cfg_override = json.loads(inline)
    if file_:
        cfg_override.update(  # file beats inline
            load_peagen_toml(Path(file_), required=True)
        )

    # ─────────────────────── 2) build Task model ────────────────────────
    if repo is None:
        raise typer.BadParameter("--repo is required for remote sorting")

    args = {
        "projects_payload": yaml_text,  # ← inline text
        "project_name": project_name,
        "start_idx": start_idx,
        "start_file": start_file,
        "transitive": transitive,
        "show_dependencies": show_dependencies,
        "repo": repo,
        "ref": ref,
    }
    task = {
        "pool": "default",
        "payload": {
            "action": "sort",
            "args": args,
            "cfg_override": cfg_override,
        },
    }

    # 2) Build Task.submit envelope using Task fields
    try:
        data = rpc_post(
            ctx.obj.get("gateway_url"),
            TASK_SUBMIT,
            task,
            timeout=10.0,
        )
        if data.error:
            typer.echo(f"[ERROR] {data.error}")
            raise typer.Exit(1)
        typer.echo(f"Submitted sort → taskId={data.result['taskId']}")
    except Exception as exc:
        typer.echo(
            f"[ERROR] Could not reach gateway at {ctx.obj.get('gateway_url')}: {exc}"
        )
        raise typer.Exit(1)
