## 6 · Worker Fabric

This section formalises how **tasks are executed** once they leave the queue.
The fabric has two cooperating actors:

* **Warm-Spawner** – a long-lived manager that guarantees a buffer of *idle capacity*.
* **One-Shot Worker** – a short-lived container/process that handles **exactly one task** and then exits, guaranteeing a pristine runtime for every job.

```
TaskQueue ────► Warm-Spawner  ────► (N) One-Shot Workers
                (always on)            (each exits after 1 task)
```

---

### 6.1  Warm-Spawner (MGR)

| Concern                | Detail                                                                                                                                                                                                            |
| ---------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Lifetime**           | 1 pod / service per capability class (e.g. `cpu`, `gpu`).                                                                                                                                                         |
| **Loop**               | 1️⃣ Poll queue depth & idle workers every `poll_ms`.<br>2️⃣ If `pending > live_capacity – warm_pool`, launch additional workers.<br>3️⃣ If `live_idle > warm_pool`, do **nothing** – workers self-exit when idle. |
| **Launch mechanism**   | `docker run` / `kubectl run` with environment shown below.                                                                                                                                                        |
| **Down-scale**         | When no task seen for `idle_timeout`, live workers exit; spawner itself is left running for near-zero idle cost.                                                                                                  |
| **Crash-reclaim**      | Runs `queue.requeue_orphans(idle_ms)` inside the same loop.                                                                                                                                                       |
| **Observable metrics** | `warm_spawner_live_workers`, `warm_spawner_idle_workers`, `warm_spawner_launch_total`.                                                                                                                            |

#### Example spawner config (`spawner.toml`)

```toml
[spawner]
queue_url   = "redis://broker:6379/0"
caps        = ["cpu","docker"]
warm_pool   = 2          # keep two idle workers ahead
max_parallel = 50        # max workers spawned at once
poll_ms     = 1000
worker_image= "ghcr.io/swarmauri/peagen-worker:latest"
```

For local testing you can set ``queue_url = "stub://"`` to use the
in-memory ``StubQueue``.

---

### 6.2  One-Shot Worker

| Environment Var      | Purpose                                      | Example                                |
| -------------------- | -------------------------------------------- | -------------------------------------- |
| `QUEUE_URL`          | Broker connection string                     | `redis://broker:6379/0`                |
| `WORKER_CAPS`        | Comma-sep capability tags                    | `cpu,docker,llm`                       |
| `WORKER_PLUGINS`     | Optional allow-list of handlers              | `MutateHandler,ExecuteDockerHandler`   |
| `WORKER_CONCURRENCY` | Parallel tasks inside the pod (threads/proc) | `1` (default) – **one task then exit** |
| `WORKER_IDLE_EXIT`   | Idle seconds before self-exit (safety)       | `600`                                  |

#### Skeleton (simplified)

```python
def main():
    queue = get_queue()
    task   = queue.pop(block=True)                     # claim exactly 1
    handler = pick_handler(task)                       # capability match
    result  = handler.handle(task)                     # run domain logic
    queue.push_result(result); queue.ack(task.id)
    sys.exit(0)
```

*If handler needs a deeper sandbox it can spawn `docker run --rm` or
Firecracker inside the pod.*
All stdout/stderr pipe into the worker logger (ComponentBase).
*Handlers may perform internal fan-outs.* For example `LLMEnsemble` can issue the same prompt to multiple LLMs in parallel. Such sub-requests are collapsed before returning a single `Result`, keeping the task atomic from the queue’s viewpoint.

---

### 6.3  Capability Matching Algorithm

```
CLAIM RULE:  task.requires  ⊆  WORKER_CAPS
HANDLER RULE: task.requires ⊆ handler.PROVIDES ⊆ WORKER_CAPS
```

* Worker ignores tasks that need unavailable caps.
* Inside the worker, first handler that satisfies rule handles the task; if none, task is re-queued.

---

### 6.4  Lifecycle & Self-Recycle

| Trigger                                      | Action                                                |
| -------------------------------------------- | ----------------------------------------------------- |
| **Task finished**                            | Worker exits (`0`).                                   |
| **Idle > WORKER\_IDLE\_EXIT**                | Worker exits (`0`) – spawner may respawn later.       |
| **Max uptime reached** (`WORKER_MAX_UPTIME`) | Finish current task → exit (`0`).                     |
| **Uncaught exception**                       | Exit (`1`); task remains un-ACK’ed → queue re-claims. |
| **SIGTERM** (cluster scale-down)             | Finish running task, ACK, exit.                       |

Workers publish a heartbeat hash `worker:<uuid>` every 15 s so Ops can detect stuck pods.

---

### 6.5  Security & Isolation

* **User-generated code** always runs *inside* a nested sandbox (Docker-in-Docker or Firecracker) **inside** the worker pod.
* Worker pod runs non-root, seccomp-profile.
* Files are mounted read-only (`/app`) except for `/tmp` scratch.
* Network egress for LLM tasks limited by outbound ACL if required.

---

### 6.6  Observability

| Metric (Prometheus)          | Source         | Description                            |
| ---------------------------- | -------------- | -------------------------------------- |
| `worker_task_total{status}`  | worker         | Count of handled tasks.                |
| `worker_runtime_seconds`     | worker         | Wall-clock per task.                   |
| `worker_exit_reason{reason}` | worker         | `success`, `idle`, `error`, `timeout`. |
| `warm_spawner_live_workers`  | spawner        | Current # container replicas.          |
| `queue_pending_total{kind}`  | queue exporter | Tasks waiting by kind.                 |

Alerts: `queue_pending_total{kind="execute"} > 50 for 10m` triggers “scale GPU pool”.
Workers log through the shared `ComponentBase` infrastructure. Under the hood
this relies on `HandlerBase` and `FormatterBase` so deployments can route logs to
Loki/Elastic or adjust message layouts. The optional `SimpleTracer` utility can
wrap handler execution to record trace IDs alongside metrics and logs.

---

### 6.7  Example Launch Commands

**Development (no Redis)**

```bash
export QUEUE_URL=stub://
peagen worker start --no-detach  # spins inline worker thread
```

**CPU cluster node**

```bash
docker run -d \
  -e QUEUE_URL=redis://broker:6379/0 \
  -e WORKER_CAPS=cpu,docker,llm \
  -e WORKER_CONCURRENCY=1 \
  ghcr.io/swarmauri/peagen-worker:latest
```

**GPU node**

```bash
docker run --gpus all -d \
  -e QUEUE_URL=redis://broker:6379/0 \
  -e WORKER_CAPS=gpu,cuda11,docker \
  -e WORKER_PLUGINS=ExecuteGPUHandler \
  ghcr.io/swarmauri/peagen-worker:latest
```

Spawner manifest (Kubernetes):

```yaml
apiVersion: apps/v1
kind: Deployment
metadata: {name: warm-spawner-cpu}
spec:
  replicas: 1
  template:
    spec:
      containers:
      - name: spawner
        image: ghcr.io/swarmauri/peagen-spawner:latest
        env:
        - {name: QUEUE_URL, value: "redis://broker:6379/0"}
        - {name: WORKER_CAPS, value: "cpu,docker"}
        - {name: WARM_POOL, value: "2"}
```

---

### 6.8  Testing & Validation

1. **Unit-test**: Mock queue, assert worker exits after one task, `Result` stored.
2. **Integration**: Spin Redis, start spawner, push 10 tasks → expect 10 worker pods created and destroyed, queue empty.
3. **Fault injection**: Kill worker mid-task; ensure spawner `XAUTOCLAIM` re-queues and new worker completes.

The Worker Fabric thus balances **always-ready** responsiveness with **fresh-environment** execution, satisfies security requirements, and provides clear knobs for scale-out and cost control.
