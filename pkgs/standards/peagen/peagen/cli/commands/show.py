from __future__ import annotations

import json
from pathlib import Path
import typer

from peagen.plugins.vcs.git_vcs import GitVCS


show_app = typer.Typer(help="Inspect git objects.")


@show_app.command("show")
def show(
    oid: str = typer.Argument(..., help="Object ID"),
    repo: Path = typer.Option(".", "--repo", help="Repository path"),
) -> None:
    """Print type, size and pretty content for *OID*."""
    vcs = GitVCS.open(repo)
    info = {
        "type": vcs.object_type(oid),
        "size": vcs.object_size(oid),
        "pretty": vcs.object_pretty(oid),
    }
    typer.echo(json.dumps(info, indent=2))
