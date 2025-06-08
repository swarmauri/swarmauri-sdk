## 3 · System-Level Architecture

### 3.1  High-Level Component Map

```
┌──────────────────────────────  User/CLI Layer  ───────────────────────────────┐
│                                                                              │
│  peagen render  peagen mutate  peagen evolve step/run  peagen worker start   │
│       │                   │                         │                       │
└───────▼───────────────────▼─────────────────────────▼────────────────────────┘
                    (A) enqueue Tasks                 (E) spawn workers

┌────────────────────────────── Core Control Plane ────────────────────────────┐
│                                                                              │
│  ┌────────────────┐    (B) Task,Result streams   ┌───────────────────────┐   │
│  │  TaskQueue     │ <───────────────────────────► │   ResultBackend       │   │
│  │  (Redis 7.x)   │                              │   (FS/S3/PG)          │   │
│  └────▲─────▲─────┘                              └──────▲────────▲────────┘   │
│       │     │                                         │        │             │
│  (C) pop   push                                   (C1) ack  (C2) store JSON  │
│       │     │                                         │        │             │
│  ┌────▼─────▼────┐                             ┌──────┴────────┴────────┐    │
│  │ Warm-Spawner   │───────(E) docker/k8s run──►│  One-Shot Worker Pods   │    │
│  │  (always-on)   │                             │  (exit after 1 task)   │    │
│  └────────────────┘                             └─────────▲──────────────┘    │
│                                                          │ (D) handle task    │
└───────────────────────────────────────────────────────────┴────────────────────┘
```

Legend
A. CLI creates **Task** objects and pushes them to **TaskQueue**
B. Queue stores Tasks and Results in Redis **Streams** (`peagen.tasks`, `peagen.results`)
C. Workers **claim** a task, **ACK** on success; on crash, Redis PEL + `XAUTOCLAIM` returns it to queue.
D. Worker runs the matching **TaskHandler** (Mutator / Executor / Renderer / Evaluator) in-process, isolated by its own container.
E. **Warm-Spawner** keeps *N* idle one-shot worker pods ahead of demand; spawns new pods when queue depth or capability demand rises.

---

### 3.2  Detailed Data Flow per Workflow

| Step | Render                                                                              | Mutate                                                                                | Evolve Generation                                                       |
| ---- | ----------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------- | ----------------------------------------------------------------------- |
| 1    | CLI pushes `RenderTask` (`requires={"cpu"}`)                                        | CLI pushes `MutateTask` (`{"llm","cpu"}`)                                             | CLI pushes chain: `Mutate`→`Execute`→`Evaluate`                         |
| 2    | CPU Render worker claims → `RenderHandler` → writes files → `Result(workspace_uri)` | Mutate worker claims → `PatchMutator` produces **ExecuteTask** → pushes back to queue | Same as Mutate + Execute: sandbox run → metrics → **EvaluateTask**      |
| 3    | Orchestrator waits `queue.wait(task_id)` → uses workspace                           | CLI prints child src path                                                             | Evaluate worker returns fitness → Orchestrator updates EvoDB; loop ends |

*Concurrency & isolation:* every handler run happens in a pod that lives for **exactly one task**; environment is pristine each time.
*Internal fan-out:* Certain handlers (e.g. the `LLMEnsemble` used during `MutateTask`) may fire off parallel sub-requests to multiple LLM back-ends. This happens entirely inside one worker container and collapses back into a single `Result`, so the queue still processes a linear chain of Tasks.
---

### 3.3  Trust & Isolation Boundaries

| Boundary                | Security Mechanism                                                                                                                    |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| **Worker Pod ↔ Host**   | Runs non-root; tmpfs volume only.                                                                                                     |
| **Handler ↔ User code** | For `ExecuteTask`, handler uses *nested* `docker run --rm` (or Firecracker) so untrusted LLM-generated Python cannot touch worker FS. |
| **Queue ↔ Worker**      | TLS for Redis (in prod); consumer group auth.                                                                                         |
| **ResultBackend**       | Write-only role for workers; orchestrator has read-only + promote.                                                                    |

---

### 3.4  Scaling Paths

| Layer             | Scale knob                       | Max (MVP)      |
| ----------------- | -------------------------------- | -------------- |
| TaskQueue (Redis) | CPU cores of broker              | \~50k msgs/s   |
| Warm-Spawner      | HPA replicas                     | 20 spawners    |
| One-Shot Workers  | HPA target=`queue_pending_total` | 256 pods       |
| LLM Ensemble      | Back-end parallelism             | vendor-limited |

---

### 3.5  Failure & Recovery

* **Worker crash before ACK** → task remains in Redis PEL → `XAUTOCLAIM` returns after `idle > 60s`.
* **Spawner crash** → K8s Deployment recreates; idle workers keep draining.
* **Queue outage** → CLI detects push failure, exits non-zero; tasks on disk can be retried.
* **ResultBackend outage** → worker returns `Result(status="error")`; orchestrator re-queues task or dead-letters after N attempts.

---

### 3.6  Component Responsibilities

| Component             | Owns                                          | Never Does                                          |
| --------------------- | --------------------------------------------- | --------------------------------------------------- |
| **CLI/Orchestrator**  | Create tasks, wait for results, EvoDB logic   | Execute user code, call LLM directly in evolve mode |
| **TaskQueue Adapter** | Delivery guarantees, ACK semantics            | Know task semantics                                 |
| **Warm-Spawner**      | Capacity management, pod lifecycle            | Handle tasks                                        |
| **One-Shot Worker**   | Capability match, handler dispatch, isolation | Keep state between tasks                            |
| **TaskHandler**       | Domain logic (mutate, exec, eval, render)     | Network with queue directly                         |
| **ResultBackend**     | Persist Result JSON, expose listing API       | Business logic                                      |

---

### 3.7  Technology Stack (MVP)

| Concern           | Choice                                              | Rationale                                             |
| ----------------- | --------------------------------------------------- | ----------------------------------------------------- |
| Broker            | **Redis Streams 7.x**                               | Built-in PEL, `XAUTOCLAIM`, single binary, good perf. |
| Container Runtime | **Docker** (rootless)                               | Developer familiarity, GPU plugin available.          |
| Metrics           | **Prometheus + Grafana** via OpenTelemetry          | Unified across Peagen core & workers.                 |
| Orchestration     | **Docker Compose** for dev; **Kubernetes** for prod | Compose is zero-install; K8s provides HPA & RBAC.     |

This architecture section defines the fixed **responsibility boundaries** and data flows all subsequent implementation sections rely on.
