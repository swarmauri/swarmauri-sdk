"""peagen.handlers.init_handler
===============================

Asynchronous entry-point for initialisation tasks.

The handler accepts either a plain dictionary or a :class:`peagen.orm.Task`
and delegates to :mod:`peagen.core.init_core`.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from peagen.core import init_core
from peagen.orm import Task
from . import ensure_task


async def init_handler(task_or_dict: Dict[str, Any] | Task) -> Dict[str, Any]:
    """Dispatch to the correct init function based on ``kind``."""
    task = ensure_task(task_or_dict)
    payload = task.payload
    args: Dict[str, Any] = payload.get("args", {})
    kind = args.get("kind")
    if not kind:
        raise ValueError("'kind' argument required")

    path = Path(args.get("path", ".")).expanduser()

    if kind == "project":
        return init_core.init_project(
            path=path,
            template_set=args.get("template_set", "default"),
            provider=args.get("provider"),
            with_doe=args.get("with_doe", False),
            with_eval_stub=args.get("with_eval_stub", False),
            force=args.get("force", False),
            git_remotes=args.get("git_remotes"),
            filter_uri=args.get("filter_uri"),
            add_filter_config=args.get("add_filter_config", False),
        )

    if kind == "template-set":
        return init_core.init_template_set(
            path=path,
            name=args.get("name"),
            org=args.get("org"),
            use_uv=args.get("use_uv", True),
            force=args.get("force", False),
        )

    if kind == "doe-spec":
        return init_core.init_doe_spec(
            path=path,
            name=args.get("name"),
            org=args.get("org"),
            force=args.get("force", False),
        )

    if kind == "ci":
        return init_core.init_ci(
            path=path,
            github=args.get("github", True),
            force=args.get("force", False),
        )

    if kind == "repo":
        return init_core.init_repo(
            repo=args.get("repo"),
            pat=args.get("pat"),
            description=args.get("description", ""),
            deploy_key=Path(args["deploy_key"]) if args.get("deploy_key") else None,
            path=Path(args["path"]) if args.get("path") else None,
            remotes=args.get("remotes"),
        )

    if kind == "repo-config":
        return init_core.configure_repo(
            path=path,
            remotes=args.get("remotes", {}),
        )

    raise ValueError(f"Unknown init kind '{kind}'")
