from __future__ import annotations

import json
from pathlib import Path

import typer
from peagen.core.git_repo_core import open_repo  # ← new import

show_app = typer.Typer(help="Inspect raw Git objects inside a repository.")


@show_app.command("show")
def show(
    oid: str = typer.Argument(..., help="Git object ID (commit, tree, blob, tag)"),
    repo: Path = typer.Option(
        ".",
        "--repo",
        "-r",
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        help="Path to the local Git repository",
    ),
) -> None:
    """
    Display the object’s **type**, **size**, and a pretty-printed representation
    of its contents.  Uses the pluggable VCS adapter exposed via
    ``peagen.core.git_repo_core.open_repo``.
    """
    vcs = open_repo(repo)  # open local clone (read-only)
    info = {
        "type": vcs.object_type(oid),
        "size": vcs.object_size(oid),
        "pretty": vcs.object_pretty(oid),
    }
    typer.echo(json.dumps(info, indent=2))
