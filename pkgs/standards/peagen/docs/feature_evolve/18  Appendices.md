## 18 · Appendices

---

### **Appendix A — Example `.peagen.toml` Files**

#### A-1  *Laptop / Offline (StubQueue)*

```toml
# .peagen.toml  – works with no Docker or Redis
[task_queue]
provider   = "stub"          # in-memory

[mutate]
target_file = "examples/bad_sort.py"
entry_fn    = "sort"

[evolve]
selector     = "epsilon"
backend      = "docker"      # still allowed if Docker present
entry_fn     = "sort"
[evolve.stop]
max_generations = 50
```

#### A-2  *Small CPU Farm (Redis Streams)*

```toml
[task_queue]
provider   = "redis"
url        = "redis://redis:6379/0"
idle_ms    = 60000
max_retry  = 3

[result_backend]
provider   = "fs"
root       = "/var/peagen/results"

[worker.defaults]
caps        = "cpu,docker,llm"
warm_pool   = 2
concurrency = 1

[llm.backend_weights]
openai = 2
groq   = 1
```

#### A-3  *Hybrid GPU + CPU Cluster*

```toml
# Additional GPU-only execution
[evolve]
backend = "gpu"              # EXECUTE tasks tagged accordingly

[[llm.backends]]
name        = "openai"
model       = "gpt-4o"
weight      = 1
api_key_env = "OPENAI_API_KEY"
timeout_ms  = 30000
```

---

### **Appendix B — Prometheus Metric Catalogue**

| Metric                           | Type      | Labels              | Emitted by    | Description                             |
| -------------------------------- | --------- | ------------------- | ------------- | --------------------------------------- |
| `queue_pending_total`            | gauge     | `stream`, `kind`    | Queue adapter | Current number of tasks waiting.        |
| `queue_pending_idle_max_seconds` | gauge     | `stream`            | Queue adapter | Oldest pending message idle time.       |
| `worker_task_total`              | counter   | `handler`, `status` | Worker        | Count of tasks per handler and outcome. |
| `worker_exit_reason_total`       | counter   | `reason`            | Worker        | `success`, `idle`, `error`, `timeout`.  |
| `handler_duration_seconds`       | histogram | `handler`, `status` | Handler       | Wall-clock runtime of `handle()`.       |
| `handler_fail_total`             | counter   | `handler`, `reason` | Handler       | Application-level failures.             |
| `llm_tokens_total`               | counter   | `backend`           | LLM Ensemble  | Prompt + completion tokens billed.      |
| `warm_spawner_live_workers`      | gauge     | `caps`              | Spawner       | Currently running one-shot worker pods. |
| `evo_best_speed_ms`              | gauge     | `workspace`         | Orchestrator  | Speed of current champion variant.      |

---

### **Appendix C — JSON Schemas**

*(Draft-07; stored under `schemas/` folder for automated validation.)*

#### C-1  `Task`

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Peagen Task",
  "type": "object",
  "required": ["kind", "id", "payload", "requires", "attempts", "created_at", "schema_v"],
  "properties": {
    "kind": { "type": "string", "enum": ["render","mutate","execute","evaluate"] },
    "id":   { "type": "string", "pattern": "^[0-9a-f]{16,}$" },
    "payload":  { "type": "object" },
    "requires": { "type": "array", "items": { "type": "string" } },
    "attempts": { "type": "integer", "minimum": 0 },
    "created_at": { "type": "string", "format": "date-time" },
    "schema_v":  { "type": "integer", "minimum": 1 }
  }
}
```

#### C-2  `Result`

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Peagen Result",
  "type": "object",
  "required": ["task_id","status","data","created_at","attempts"],
  "properties": {
    "task_id":   { "type": "string" },
    "status":    { "type": "string", "enum": ["ok","error","skip"] },
    "data":      { "type": "object" },
    "created_at":{ "type": "string", "format": "date-time" },
    "attempts":  { "type": "integer", "minimum": 1 }
  }
}
```

---

### **Appendix D — Kubernetes Reference Manifests**

#### D-1  Redis Broker (for dev)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata: {name: redis-broker}
spec:
  replicas: 1
  selector: {matchLabels: {app: redis-broker}}
  template:
    metadata: {labels: {app: redis-broker}}
    spec:
      containers:
      - name: redis
        image: redis:7-alpine
        args: ["--save","\", \"--appendonly","no"]
        resources: {limits: {memory: "512Mi"}}
---
apiVersion: v1
kind: Service
metadata: {name: redis}
spec:
  selector: {app: redis-broker}
  ports: [{port: 6379, targetPort: 6379}]
```

#### D-2  Warm-Spawner Deployment (CPU)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata: {name: peagen-spawner-cpu}
spec:
  replicas: 1
  selector: {matchLabels:{app: peagen-spawner, caps: cpu}}
  template:
    metadata: {labels:{app: peagen-spawner, caps: cpu}}
    spec:
      containers:
      - name: spawner
        image: ghcr.io/swarmauri/peagen-spawner:latest
        env:
          - {name: QUEUE_URL, value: "redis://redis:6379/0"}
          - {name: WORKER_CAPS, value: "cpu,docker,llm"}
          - {name: WARM_POOL,  value: "2"}
```

#### D-3  Worker Image (GPU) DaemonSet

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata: {name: peagen-worker-gpu}
spec:
  selector: {matchLabels:{app: peagen-worker, caps: gpu}}
  template:
    metadata: {labels:{app: peagen-worker, caps: gpu}}
    spec:
      tolerations: [{key: "nvidia.com/gpu", operator: "Exists"}]
      containers:
      - name: worker
        image: ghcr.io/swarmauri/peagen-worker:latest
        env:
          - {name: QUEUE_URL, value: "redis://redis:6379/0"}
          - {name: WORKER_CAPS, value: "gpu,cuda11,docker"}
          - {name: WORKER_PLUGINS, value: "ExecuteGPUHandler"}
        resources: {limits: {"nvidia.com/gpu": 1}}
```

---

### **Appendix E — Security & Pen-Test Checklist**

| Check                                                                    | Tool / Method                                        |
| ------------------------------------------------------------------------ | ---------------------------------------------------- |
| Verify worker runs as non-root UID ≠ 0                                   | `kubectl exec id`                                    |
| Confirm sandbox has no outbound network (Execute)                        | `curl 8.8.8.8` inside container should fail          |
| Run `bandit -r src` – 0 High issues                                      | CI job                                               |
| Scan Docker images with Trivy – 0 Critical vulns                         | `make trivy-scan`                                    |
| Kill worker mid-task – orphan reclaimed                                  | Chaos test harness                                   |
| LLM prompt injection test (upload `__import__('os').system('rm -rf /')`) | Should be blocked by seccomp & no volume permissions |


---

### **Appendix F — Parent Selector Strategies**

The Adaptive-ε method is the default selection strategy. Additional selectors can be implemented by registering an entry point under `peagen.parent_selectors`:

- **Upper Confidence Bound (UCB)** – balances mean fitness and sampling frequency.
- **Tournament selection** – draws multiple candidates and chooses the best.
- **Rank-based or fitness-proportional** – weights selection odds by program fitness.
- **Thompson sampling** – applies Bayesian bandit exploration.
- **Age-based or lexicase** – promotes diverse or younger parents.

Each implementation must fulfill the `ParentSelector` interface and retrieve programs via the EvoDB repository API.

---

These appendices complete the technical brief with **ready-to-use artifacts**:
sample configs, metric reference, schemas for validation, deployment manifests,
and a checklist for security sign-off.
