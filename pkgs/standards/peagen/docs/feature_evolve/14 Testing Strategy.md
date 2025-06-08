## 14 · Testing Strategy

A multi-layer test plan ensures that Peagen’s new task-fabric is **correct,
deterministic, performant, and failure-tolerant**—from a single Python class
to the full swarm in Kubernetes.

| Layer                    | Focus                                                | Tools                                          | Frequency                    |
| ------------------------ | ---------------------------------------------------- | ---------------------------------------------- | ---------------------------- |
| **Unit**                 | Logic in isolation (handlers, selectors, EvoDB ops). | `pytest`, `hypothesis`, `pytest-mypy-plugins`  | Every PR (GitHub Actions)    |
| **Static**               | Typing, style, imports.                              | `mypy --strict`, `ruff`, `bandit`              | Every PR                     |
| **Contract**             | Dataclass → MessagePack round-trip, `schema_v`.      | `pytest` golden vectors                        | Every PR                     |
| **Integration (Stub)**   | TaskQueue + InlineWorker, no externals.              | `pytest -m integration_stub`                   | Every commit on **mono/dev** |
| **Integration (Redis)**  | Redis Streams, Warm-Spawner, containerised workers.  | Docker Compose + `pytest -m integration_redis` | Nightly                      |
| **Performance Bench**    | Targets PT-1 .. PT-4 (Section 12).                   | Benchmark harness, Prom scrape                 | Nightly on CPU-32 host       |
| **E2E Smoke**            | Full CLI path on GPU pool.                           | GitHub self-hosted runner (A100)               | Weekly                       |
| **Chaos / Fault**        | Orphan requeue, DLQ rollover, LLM 503.               | `pytest-chaos`, fault-injection scripts        | Weekly                       |
| **Replay / Determinism** | Checkpoint replay ± 1 %.                             | `bench_replay.py`                              | Release gate                 |

---

### 14.1  Unit-Test Guidelines

* One test file per module (`test_<module>.py`).
* Use **frozen random seed** (`seed(0xA11A)`) when randomness unavoidable.
* **Never** hit external LLM: mock `LLMEnsemble.generate` with fixed diff.
* Cover edge-cases (`attempts` overflow, empty diff, bucket collision).
* ≥ 90 % branch coverage on `peagen.*` (enforced by `pytest-cov`).

Example:

```python
def test_patch_mutator_happy(monkeypatch, sample_parent):
    def fake_generate(prompt, **_): return "+print('hi')"
    monkeypatch.setattr(LLMEnsemble, "generate", fake_generate)
    task   = Task.new(TaskKind.MUTATE, {"parent_src": sample_parent,"entry_fn":"f"})
    result = PatchMutator(...).handle(task)
    assert result.status == "ok"
    assert "spawn" in result.data
```

---

### 14.2  Stub-Queue Integration

* Spin **StubQueue**; start **InlineWorker** (`InlineWorker(queue).run_once()`).
* Push `RenderTask`, assert output files exist; check `queue_pending_total==0`.
* CI job name: **`integration-stub.yml`** (runs < 10 s).

---

### 14.3  Redis + Container Integration

* Bring up `docker-compose -f ci/docker-redis.yml`.
* Launch Warm-Spawner + 4 workers (cpu).
* Execute `peagen evolve step`.
* Assert:

  * Result speed populated.
  * `worker_exit_reason{reason="success"}==5`.
  * `redis XINFO STREAM peagen.tasks len == 0`.

---

### 14.4  Benchmark Harness

* Located in `benchmarks/`.
* Runs workloads in **dedicated bare-metal hosts** (see Section 12).
* Emits CSV & Prom snapshot; GitHub Action uploads artifact.
* `perf.regression` job fails if:

  * PT-1 > 105 % of baseline.
  * PT-2 latency > SLA.
  * PT-3 throughput < 90 % of baseline.

---

### 14.5  Chaos Tests

| Fault injected                              | Expectation                                                         |
| ------------------------------------------- | ------------------------------------------------------------------- |
| Kill worker PID mid-execute                 | Task reclaimed and completes on new worker within 2 × `idle_ms`.    |
| Delete Redis primary for 10 s               | CLI exits non-zero; no task duplication; DLQ empty.                 |
| LLM backend returns HTTP 503 for 5 requests | MutateHandler retries (attempts++) then succeeds; no infinite loop. |

Executed by `pytest -m chaos`, uses `docker kill`, Redis Sentinel failover, and monkey-patching LLM.

---

### 14.6  Replay / Determinism Test

1. Run `peagen evolve run --generations 30 --sync --checkpoint ckpt.msgpack`.
2. Delete `winner.py`.
3. Run `peagen evolve step --sync --resume`.
4. Assert best-speed within ±1 % of previous run.

Ensures EvoDB restoration & seed propagation are correct.

---

### 14.7  CI Pipeline Overview

```
name: Peagen CI
on: [push, pull_request]
jobs:
  lint:
  unit:
  integration_stub:
  typecheck:
  build-image:
  integration_redis:
      needs: [build-image]
  benchmark:
      if: schedule == nightly
  release_gate:
      needs: [benchmark]
      if: tag push
```

---

### 14.8  Contribution Checklist

* New handler must include **unit test**, **capability docstring**, **metrics**.
* New plugin must have **integration stub** test.
* PR template requires ticking: “Adds tests & docs”.

---

This layered testing strategy provides **fast feedback for developers**,
**confidence for release engineering**, and **measurable regress-guards** for
product & ops stakeholders.
