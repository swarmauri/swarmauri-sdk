from __future__ import annotations

import typer

from peagen.worker import OneShotWorker, WorkerConfig
from peagen.spawner import SpawnerConfig, WarmSpawner

worker_app = typer.Typer(help="Manage Peagen workers")


@worker_app.command("start")
def start_worker(
    caps: str = typer.Option("", "--caps", envvar="WORKER_CAPS", help="Capability tags"),
    plugins: str = typer.Option("", "--plugins", envvar="WORKER_PLUGINS", help="Allowed task handlers"),
    concurrency: int = typer.Option(1, "--concurrency", envvar="WORKER_CONCURRENCY", help="Parallel tasks"),
    warm_pool: int = typer.Option(0, "--warm-pool", help="Maintain N idle workers"),
    exit_after_idle: int = typer.Option(600, "--exit-after-idle", envvar="WORKER_IDLE_EXIT", help="Seconds before exit"),
    config: str = typer.Option("spawner.toml", "--config", help="Spawner config file"),
) -> None:
    """Launch a worker or warm-spawner depending on ``--warm-pool``."""
    if warm_pool > 0:
        sp_cfg = SpawnerConfig.from_toml(config)
        sp_cfg.warm_pool = warm_pool
        if caps:
            sp_cfg.caps = [c.strip() for c in caps.split(",") if c.strip()]
        WarmSpawner(sp_cfg).run()
    else:
        cfg = WorkerConfig.from_env()
        if caps:
            cfg.caps = set(c.strip() for c in caps.split(",") if c.strip())
        if plugins:
            cfg.plugins = set(p.strip() for p in plugins.split(",") if p.strip())
        cfg.concurrency = concurrency
        cfg.idle_exit = exit_after_idle
        OneShotWorker(cfg).run()
