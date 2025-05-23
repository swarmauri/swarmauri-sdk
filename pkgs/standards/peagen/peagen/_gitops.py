"""Utilities for interacting with Git repositories."""

import typer
import subprocess
import tempfile
from pathlib import Path

print("WARNING DEPRECATING")


def _clone_swarmauri_repo(use_dev_branch: bool = False) -> Path:
    """
    Clones the swarmauri-sdk repository to a temporary directory.

    :param use_dev_branch: If True, clone from mono/dev branch instead of master.
    :return: Path to the cloned directory.
    """
    tmp_dir = Path(tempfile.mkdtemp(prefix="swarmauri-sdk-"))
    repo_url = "https://github.com/swarmauri/swarmauri-sdk.git"
    branch = "mono/dev" if use_dev_branch else "master"
    try:
        typer.echo(f"Starting clone of {repo_url}")
        subprocess.check_call(
            ["git", "clone", "--depth=1", "--branch", branch, repo_url, str(tmp_dir)]
        )
        typer.echo("")
        return tmp_dir
    except subprocess.CalledProcessError as e:
        typer.echo(f"[ERROR] Cloning swarmauri-sdk failed: {e}")
        raise typer.Exit(code=1)
