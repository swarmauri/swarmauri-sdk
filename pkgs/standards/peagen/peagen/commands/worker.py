from __future__ import annotations

import typer

from peagen.worker import OneShotWorker, WorkerConfig
from peagen.spawner import SpawnerConfig, WarmSpawner

worker_app = typer.Typer(help="Manage Peagen workers")


@worker_app.command("start")
def start_worker(
    warm_pool: int = typer.Option(0, "--warm-pool", help="Maintain N idle workers"),
    config: str = typer.Option("spawner.toml", "--config", help="Spawner config file"),
) -> None:
    """Launch a worker or warm-spawner depending on ``--warm-pool``."""
    if warm_pool > 0:
        sp_cfg = SpawnerConfig.from_toml(config)
        sp_cfg.warm_pool = warm_pool
        WarmSpawner(sp_cfg).run()
    else:
        cfg = WorkerConfig.from_env()
        OneShotWorker(cfg).run()
