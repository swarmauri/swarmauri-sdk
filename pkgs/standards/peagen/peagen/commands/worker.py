from __future__ import annotations

import typer

import os
import subprocess
import sys

from peagen.worker import OneShotWorker, WorkerConfig
from peagen.spawner import SpawnerConfig, WarmSpawner

worker_app = typer.Typer(help="Manage Peagen workers")


def _run_worker(warm_pool: int, config: str) -> None:
    """Run the worker or warm-spawner in the current process."""
    if warm_pool > 0:
        sp_cfg = SpawnerConfig.from_toml(config)
        sp_cfg.warm_pool = warm_pool
        WarmSpawner(sp_cfg).run()
    else:
        cfg = WorkerConfig.from_env()
        OneShotWorker(cfg).run()


@worker_app.command("start")
def start_worker(
    warm_pool: int = typer.Option(0, "--warm-pool", help="Maintain N idle workers"),
    config: str = typer.Option("spawner.toml", "--config", help="Spawner config file"),
    detach: bool = typer.Option(True, "--detach/--no-detach", help="Run in background"),
) -> None:
    """Launch a worker or warm-spawner depending on ``--warm-pool``."""
    if detach:
        cmd = [
            sys.executable,
            "-m",
            "peagen.cli",
            "worker",
            "start",
            f"--warm-pool={warm_pool}",
            f"--config={config}",
            "--no-detach",
        ]
        subprocess.Popen(
            cmd,
            env=os.environ.copy(),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        typer.echo("Worker detached")
    else:
        _run_worker(warm_pool, config)
