from __future__ import annotations

import os
import subprocess
import sys
import time
from dataclasses import dataclass
from typing import List

from peagen.queue import make_queue


@dataclass
class SpawnerConfig:
    queue_url: str
    caps: List[str]
    warm_pool: int = 2
    max_parallel: int = 10
    poll_ms: int = 1000
    worker_image: str = "peagen-worker:latest"
    idle_ms: int = 60000

    @classmethod
    def from_toml(cls, path: str) -> "SpawnerConfig":
        import tomllib

        with open(path, "r", encoding="utf-8") as f:
            data = tomllib.loads(f.read())
        cfg = data.get("spawner", {})
        return cls(
            queue_url=cfg.get("queue_url", "stub://"),
            caps=cfg.get("caps", []),
            warm_pool=int(cfg.get("warm_pool", 2)),
            max_parallel=int(cfg.get("max_parallel", 10)),
            poll_ms=int(cfg.get("poll_ms", 1000)),
            worker_image=cfg.get("worker_image", "peagen-worker:latest"),
        )


class WarmSpawner:
    """Very small warm-spawner implementation."""

    def __init__(self, cfg: SpawnerConfig) -> None:
        self.cfg = cfg
        provider = "redis" if cfg.queue_url.startswith("redis") else "stub"
        self.queue = make_queue(provider, url=cfg.queue_url)
        self.workers: List[subprocess.Popen] = []

    # ------------------------------------------------------------ internals
    def _launch_worker(self) -> None:
        env = os.environ.copy()
        env.update(
            QUEUE_URL=self.cfg.queue_url,
            WORKER_CAPS=",".join(self.cfg.caps),
        )
        cmd = [sys.executable, "-m", "peagen.cli", "worker", "start", "--no-detach"]
        p = subprocess.Popen(cmd, env=env)
        self.workers.append(p)

    def _cleanup_workers(self) -> int:
        live = []
        idle = 0
        for p in self.workers:
            if p.poll() is None:
                live.append(p)
            else:
                idle += 1
        self.workers = live
        return idle

    # ------------------------------------------------------------ main loop
    def run(self) -> None:
        while True:
            pending = getattr(self.queue, "pending_count", lambda: 0)()
            self._cleanup_workers()
            live = len(self.workers)

            desired = min(
                self.cfg.max_parallel,
                max(self.cfg.warm_pool, pending + self.cfg.warm_pool),
            )
            to_launch = max(0, desired - live)
            for _ in range(to_launch):
                self._launch_worker()

            self.queue.requeue_orphans(self.cfg.idle_ms)
            time.sleep(self.cfg.poll_ms / 1000)


__all__ = ["WarmSpawner", "SpawnerConfig"]
