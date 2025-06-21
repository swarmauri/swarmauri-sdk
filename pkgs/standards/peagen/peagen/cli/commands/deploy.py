from __future__ import annotations

import io
from pathlib import Path

import paramiko
import pygit2
import typer

from peagen.secrets import AutoGpgDriver
from peagen.cli.commands.secrets import _load, _save


deploy_app = typer.Typer(help="Manage SSH deploy keys and push commits.")


@deploy_app.command("add-key")
def add_key(name: str, key_file: Path) -> None:
    """Encrypt *key_file* and store it under *name*."""
    drv = AutoGpgDriver()
    secret = drv.encrypt(key_file.read_bytes(), []).decode()
    data = _load()
    data[name] = secret
    _save(data)
    typer.echo(f"Stored deploy key secret '{name}'")


@deploy_app.command("push")
def push(
    repo_path: Path = Path("."),
    secret_name: str = "DEPLOY_KEY",
    branch: str = "main",
    remote: str = "origin",
) -> None:
    """Push *branch* to *remote* using *secret_name* deploy key."""
    data = _load()
    cipher = data.get(secret_name)
    if not cipher:
        raise typer.BadParameter(f"Unknown secret {secret_name}")

    drv = AutoGpgDriver()
    key_text = drv.decrypt(cipher.encode()).decode()
    key = paramiko.PKey.from_private_key(io.StringIO(key_text))
    pub = f"{key.get_name()} {key.get_base64()}"

    callbacks = pygit2.RemoteCallbacks(
        credentials=pygit2.KeypairFromMemory("git", pub, key_text, "")
    )

    repo = pygit2.Repository(str(repo_path))
    repo.remotes[remote].push([f"refs/heads/{branch}"], callbacks=callbacks)
    typer.echo(f"Pushed {branch} using deploy key '{secret_name}'")
