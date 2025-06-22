import asyncio
import json
from pathlib import Path

import pgpy
import pytest

from peagen.plugins.queues.in_memory_queue import InMemoryQueue
from peagen.plugins.result_backends.in_memory_backend import InMemoryResultBackend

BASELINE_FILE = Path(__file__).with_name("benchmark.json")


def _percentile(data: list[float], pct: float) -> float:
    if not data:
        return 0.0
    data = sorted(data)
    k = int((pct / 100.0) * (len(data) - 1))
    return data[k]


def _load_baseline() -> dict:
    if BASELINE_FILE.exists():
        return json.loads(BASELINE_FILE.read_text())
    return {}


def _check_latency(name: str, p95_ms: float) -> None:
    baseline = _load_baseline().get(name)
    if baseline is not None and p95_ms > baseline * 1.1:
        pytest.fail(
            f"{name} p95 {p95_ms:.3f}ms exceeds 110% of baseline {baseline:.3f}ms"
        )


def _check_throughput(name: str, ops: float) -> None:
    baseline = _load_baseline().get(name)
    if baseline is not None and ops < baseline * 0.9:
        pytest.fail(
            f"{name} throughput {ops:.3f} req/s below 90% of baseline {baseline:.3f}"
        )


@pytest.fixture()
def gateway(monkeypatch):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    q = InMemoryQueue()

    class StubPM:
        def __init__(self, cfg):
            pass

        def get(self, group: str):
            if group == "queues":
                return q
            if group == "result_backends":
                return InMemoryResultBackend()
            return None

    import peagen.plugins

    monkeypatch.setattr(peagen.plugins, "PluginManager", StubPM)
    import peagen.gateway as gw

    import importlib

    importlib.reload(gw)

    monkeypatch.setattr(gw, "queue", q)
    monkeypatch.setattr(gw, "result_backend", InMemoryResultBackend())

    async def noop(*_args, **_kwargs):
        return None

    monkeypatch.setattr(gw, "_persist", noop)
    monkeypatch.setattr(gw, "_publish_event", noop)

    yield gw
    loop.close()
    asyncio.set_event_loop(None)


@pytest.mark.acceptance
@pytest.mark.perf
def test_login_benchmark(benchmark, gateway):
    key = pgpy.PGPKey.new(pgpy.constants.PubKeyAlgorithm.RSAEncryptOrSign, 1024)
    uid = pgpy.PGPUID.new("bench")
    key.add_uid(uid, usage={pgpy.constants.KeyFlags.Sign})
    pubkey = str(key.pubkey)

    async def run():
        await gateway.keys_upload(pubkey)

    benchmark(lambda: asyncio.run(run()))
    p95_ms = _percentile(benchmark.stats.stats.data, 95) * 1000
    _check_latency("login_p95_ms", p95_ms)


@pytest.mark.acceptance
@pytest.mark.perf
def test_secret_create_benchmark(benchmark, gateway):
    async def run():
        await gateway.secrets_add("bench", "secret")

    benchmark(lambda: asyncio.run(run()))
    p95_ms = _percentile(benchmark.stats.stats.data, 95) * 1000
    _check_latency("secret_create_p95_ms", p95_ms)


@pytest.mark.acceptance
@pytest.mark.perf
def test_task_dispatch_throughput(benchmark, gateway):
    async def run():
        await gateway.task_submit(pool="p", payload={}, taskId=None)

    benchmark(lambda: asyncio.run(run()))
    _check_throughput("task_dispatch_throughput_req_s", benchmark.stats.stats.ops)
