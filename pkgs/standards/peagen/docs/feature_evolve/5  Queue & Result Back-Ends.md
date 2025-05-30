## 5 · Queue & Result Back-Ends

This section defines the **delivery and persistence plane** that glues CLI producers, worker pods, and dashboards together.

---

### 5.1  `TaskQueue` Interface (API contract)

```python
# peagen/queue/base.py
class TaskQueue(ComponentBase, Protocol):
    # Producer
    def enqueue(self, task: Task) -> None: ...

    # Consumer
    def pop(self, block: bool = True, timeout: int = 1) -> Task | None: ...  # claim
    def ack(self, task_id: str) -> None: ...                                 # success

    # Admin
    def push_result(self, result: Result) -> None: ...
    def wait_for_result(self, task_id: str, timeout: int) -> Result | None: ...
    def requeue_orphans(self, idle_ms: int, max_batch: int) -> int: ...      # crash-recovery
```

*Guarantees*

* **At-least-once** task delivery (retries possible).
* **Exactly-once** result stream (task\_id key).
* Async-safe for multi-producer / multi-consumer.

---

### 5.2  StubQueue (dev / CI)

*Pure-Python, in-memory* – zero external deps.

```python
class StubQueue(TaskQueue):
    _todo:    deque[Task]
    _inflight:dict[str, tuple[Task,float]]   # ts claimed
    _done:    dict[str, Result]

    def requeue_orphans(self, idle_ms=60000, max_batch=50):
        now = time.time()*1000
        moved = 0
        for tid,(t,ts) in list(self._inflight.items()):
            if now-ts > idle_ms and moved<max_batch:
                self._todo.appendleft(t); del self._inflight[tid]; moved+=1
        return moved
```

*Used automatically when `provider = "stub"` or Redis unavailable.*
CI runs with InlineWorker + StubQueue for fastest feedback.

---

### 5.3  Redis Streams Adapter (production MVP)

| Feature           | Redis Command                                              |
| ----------------- | ---------------------------------------------------------- |
| **Enqueue**       | `XADD peagen.tasks * json_blob`                            |
| **Claim**         | `XREADGROUP GROUP peagen <worker-id> BLOCK 1000 COUNT 1`   |
| **ACK**           | `XACK peagen peagen <msg-id>`                              |
| **Crash-reclaim** | `XAUTOCLAIM peagen peagen <worker-id> <idle_ms> COUNT <n>` |
| **Push result**   | `XADD peagen.results * json_blob`                          |

*Stream Keys*

* `peagen.tasks`
* `peagen.results`
* `peagen.dead` (dead-letter)

*Operational Limits*

* `maxlen` set to 10 M (approx 2 GB MessagePack).
* Stream TTL: 14 days via `EXPIRE`.

*Security*

* ACL user `peagen` with commands `xadd,xreadgroup,xack,xautoclaim,xdel`.
* TLS recommended (`rediss://`).

---

#### Crash & Retry Flow

```
1. Worker claims  msg 42 → enters Pending-Entries-List
2. Worker dies    (no XACK)
3. Spawner cron:  XAUTOCLAIM ... IDLE 60000
4. Redis moves msg 42 back to min-idle consumer
5. Attempts++ in message body; if attempts > MAX_RETRY (3) → XADD peagen.dead
```

---

### 5.4  Dead-Letter Policy

| Stream        | Retention | Consumer Action                                   |
| ------------- | --------- | ------------------------------------------------- |
| `peagen.dead` | 30 days   | CLI `peagen queue dlq list` & `dlq retry/inspect` |

Product managers can export DLQ as CSV to diagnose persistent failures.

---

### 5.5  Metrics Emitted (Redis adapter)

| Metric                           | Type    | Labels           |
| -------------------------------- | ------- | ---------------- |
| `queue_pending_total`            | gauge   | `stream`, `kind` |
| `queue_pending_idle_max_seconds` | gauge   | `stream`         |
| `queue_ack_total`                | counter | `kind`           |
| `queue_dead_total`               | counter | `kind`           |

Scraped via `redis-exporter` + custom Lua collector for idle-max.

---

### 5.6  `ResultBackend` Interface

```python
class ResultBackend(ComponentBase, Protocol):
    def save(self, result: Result) -> None: ...
    def get(self, task_id: str) -> Result | None: ...
    def iter(self, kind: TaskKind | None = None): ...
```

#### 5.6.1 FSBackend (default)

```
.peagen/
   results/
      2025-06-01/
         mutate-<taskid>.msgpack
         execute-<taskid>.msgpack
```

*Uses atomic `os.replace` to ensure no partial writes.*

#### 5.6.2 Optional Back-ends

| Backend            | Use-case                           | Status  |
| ------------------ | ---------------------------------- | ------- |
| **Postgres JSONB** | Multi-tenant SaaS; SQL analytics   | backlog |
| **S3 / MinIO**     | Cheap long-term storage (>30 days) | roadmap |

---

### 5.7  Configuration Snippets

```toml
# .peagen.toml
[task_queue]
provider = "redis"
url      = "rediss://peagen:pa55@broker.internal:6379/0"
idle_ms  = 60000
max_retry = 3

[result_backend]
provider = "fs"
root     = ".peagen/results"
compress = true                 # gzip .msgpack files
```

Set `provider="stub"` for offline/dev runs.

---

### 5.8  Extending with New Brokers

*Implement* `TaskQueue` methods, register via:

```toml
[project.entry-points."peagen.task_queues"]
sqs = "my_pkg.sqs_queue:SQSQueue"
nats = "my_pkg.nats_queue:NATSQueue"
```

Must support at-least-once semantics and orphan requeue.

---

#### Take-away

* **StubQueue** gets developers productive offline.
* **Redis Streams** delivers production-grade durability, back-pressure, and retry.
* `ResultBackend` guarantees result persistence even after workers exit.

These abstractions keep CLI, orchestrator and handlers **broker-agnostic**, enabling future migration without invasive code changes.
