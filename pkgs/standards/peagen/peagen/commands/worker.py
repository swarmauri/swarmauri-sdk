from __future__ import annotations

import typer

import os
import subprocess
import sys
import psutil

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


def _find_workers() -> list[subprocess.Popen]:
    """Return running worker processes started via ``peagen worker start``."""
    import psutil

    procs = []
    for p in psutil.process_iter(["cmdline"]):
        try:
            cmd = p.info.get("cmdline") or []
        except psutil.NoSuchProcess:
            continue
        if "peagen.cli" in cmd and "worker" in cmd and "start" in cmd:
            procs.append(p)
    return procs


@worker_app.command("ps")
def list_workers(
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Show environment information"
    )
) -> None:
    """List running detached workers."""
    procs = _find_workers()
    if not procs:
        typer.echo("No workers found")
        return

    if verbose:
        typer.echo("PID\tQUEUE_URL\tWORKER_CAPS\tWARM_POOL\tCMD")
    else:
        typer.echo("PID\tCMD")

    for p in procs:
        try:
            cmd = " ".join(p.cmdline())
        except psutil.NoSuchProcess:
            continue

        if verbose:
            try:
                env = psutil.Process(p.pid).environ()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                env = {}
            queue_url = env.get("QUEUE_URL", "")
            caps = env.get("WORKER_CAPS", "")
            warm_pool = env.get("WARM_POOL", "")
            typer.echo(f"{p.pid}\t{queue_url}\t{caps}\t{warm_pool}\t{cmd}")
        else:
            typer.echo(f"{p.pid}\t{cmd}")


@worker_app.command("kill")
def kill_workers(pid: int | None = typer.Option(None, "--pid")) -> None:
    """Terminate running worker processes."""
    procs = _find_workers()
    targets = procs if pid is None else [p for p in procs if p.pid == pid]
    if not targets:
        typer.echo("No matching workers")
        return
    for p in targets:
        try:
            p.terminate()
            typer.echo(f"Killed worker {p.pid}")
        except psutil.NoSuchProcess:
            typer.echo(f"Worker {p.pid} already exited")


@worker_app.command("add")
def add_workers(
    count: int = typer.Option(1, "--count", help="Number of workers to start"),
    warm_pool: int = typer.Option(0, "--warm-pool", help="Maintain N idle workers"),
    config: str = typer.Option("spawner.toml", "--config", help="Spawner config file"),
) -> None:
    """Spawn additional detached workers."""
    for _ in range(count):
        start_worker(warm_pool=warm_pool, config=config, detach=True)
    typer.echo(f"Started {count} worker(s)")
