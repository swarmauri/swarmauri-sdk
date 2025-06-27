"""peagen.handlers.templates_handler
----------------------------------

Async handler for template-set management tasks.
"""

from __future__ import annotations

from typing import Any, Dict

from peagen._utils import maybe_clone_repo

from peagen.core.templates_core import (
    list_template_sets,
    show_template_set,
    add_template_set,
    remove_template_set,
)
from peagen.models.task import Task  # type: ignore


async def templates_handler(task: Dict[str, Any] | Task) -> Dict[str, Any]:
    """Dispatch template-set operations based on ``args.operation``."""
    payload = task.get("payload", {})
    args: Dict[str, Any] = payload.get("args", {})
    repo = args.get("repo")
    ref = args.get("ref", "HEAD")
    op = args.get("operation")

    with maybe_clone_repo(repo, ref):
        if op == "list":
            return list_template_sets()
        if op == "show":
            return show_template_set(args["name"])
        if op == "add":
            return add_template_set(
                args["source"],
                from_bundle=args.get("from_bundle"),
                editable=args.get("editable", False),
                force=args.get("force", False),
            )
        if op == "remove":
            return remove_template_set(
                args["name"],
            )

    raise ValueError(f"Unknown operation: {op}")
