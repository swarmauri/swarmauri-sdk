## 11 · Operational Concerns

This section arms infrastructure teams with **run-sheet guidance, ready-to-copy
manifests, and alert thresholds** for a smooth Day-2 experience.

---

### 11.1 Autoscaling Recipes

| Environment                                 | How to Scale Up                                                                                                                                                  | Idle Scale-Down                                                          | Notes                                        |
| ------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------ | -------------------------------------------- |
| **Docker Compose (on-prem or laptop farm)** | *watch-queue.py* script polls `queue_pending_total` every 30 s:<br>`desired = max(1, min(32, pending // 2))`<br>`docker compose up --scale worker=${desired}`    | Same script drops replicas when `pending == 0` for >5 min.               | Simple, no additional services.              |
| **Kubernetes**                              | **HorizontalPodAutoscaler** on `Deployment/peagen-worker` targeting **external metric** `redis_queue_pending{stream="peagen.tasks"}`.<br>`targetAverageValue: 5` | `minReplicas: 0`,  `behavior.scaleDown.stabilizationWindowSeconds: 300`. | Pods exit after 10 min idle; HPA frees them. |
| **AWS Fargate / ECS**                       | CloudWatch Alarm on `RedisPendingTasks ≥ 20` triggers Step-Function that launches X Fargate tasks; second alarm on `≤2` tasks for 5 min stops them.              | Same alarm resets to 0 tasks.                                            | Serverless pay-per-second.                   |
| **Systemd-only servers**                    | `systemd-run --unit=peagen-worker@$(uuidgen) …` from cron when queue depth high.                                                                                 | Idle timer in unit file `StopWhenUnneeded=yes`.                          | Works without containers.                    |

*Warm-Spawner* keeps **2 idle pods** ahead (`warm_pool = 2`) to absorb spiky
latency without the autoscaler’s cold-start penalty.

---

### 11.2 Fault-Tolerance & Crash Recovery

| Failure Mode                    | Mechanism                                                                                           | Operator Action                                                          |
| ------------------------------- | --------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| Worker pod crashes mid-task     | Message stays in Redis PEL (no `XACK`).<br>Spawner runs `XAUTOCLAIM` every 60 s → re-queues orphan. | None—automatic retry. Check `worker_exit_reason{reason="error"}` metric. |
| Mutate handler gets *LLM 503*   | Returns `Result(status="error", retryable=True)` → queue re-enqueues with `attempts+1`.             | After 3 attempts DLQ captures; inspect token balance.                    |
| Disk full on ResultBackend (FS) | `save()` raises; Worker emits `error` result.                                                       | Alert fires on `result_backend_fail_total > 0`; enlarge volume.          |
| Redis broker outage             | CLI push fails – exits non-zero; workers idle.                                                      | HA Redis / RDB-AOF; restart CLI once broker healthy.                     |
| Stuck Selector feedback loop    | EvoDB checkpoint every 10 gens; resume with different selector flag.                                | Investigate histogram of buckets.                                        |

---

### 11.3 Observability & Alerting Matrix

| Metric (Prometheus)                          | Expected Range | Alert Threshold | Action                                                  |
| -------------------------------------------- | -------------- | --------------- | ------------------------------------------------------- |
| `queue_pending_total{kind="execute"}`        | 0 – 20         | > 50 for 10 min | Scale GPU workers; inspect tasks for high failure rate. |
| `worker_exit_reason{reason="error"}`         | ≈ 0            | > 5 in 10 min   | Look at pod logs; likely image or code bug.             |
| `handler_fail_total{handler="PatchMutator"}` | < 1 % of calls | > 10 % in 5 min | LLM outage or bad prompt; fallback to other backend.    |
| `llm_tokens_total` (per backend)             | variable       | sudden 2× spike | Verify routing weights; cost alert.                     |
| `result_backend_fail_total`                  | 0              | > 0             | Storage failure.                                        |
| `redis_key_memory_bytes{key="peagen.tasks"}` | < 200 MB       | > 500 MB        | Trim stream with `MAXLEN`; investigate consumer lag.    |

Dashboards: **Main** (queue, workers, best-speed graph) and **Cost** (tokens, GPU seconds).

Logs: Structured JSON via ComponentBase logger → Loki/Elastic.
The logger builds on the repo's `HandlerBase` and `FormatterBase` classes so
operators can swap handlers or tweak log formats through configuration.
Optional distributed traces can be recorded with the `SimpleTracer` utility and
its context manager—trace IDs are then included in structured log records.

---

### 11.4 Security & Sandboxing Guidelines

| Layer                    | Control                                                                         | Rationale                                    |
| ------------------------ | ------------------------------------------------------------------------------- | -------------------------------------------- |
| Worker container         | Non-root UID, read-only root FS, seccomp `runtime/default`, `no-new-privileges` | Prevent privilege escalation.                |
| Nested sandbox (Execute) | `docker run --rm --network none --pids-limit 128 --memory 1g`                   | Isolate user code; enforce mem/CPU limits.   |
| Network egress           | LLM handlers require HTTPS; Execute sandboxes get `--network none`.             | Avoid data exfiltration from generated code. |
| Secrets                  | API keys injected via env in **worker pods only**; never in task payloads.      | Limits exposure to orchestrator logs.        |
| Audit                    | Every Result record includes `handler_version`, `image_tag`, `worker_id`.       | Forensics after incident.                    |
| SBOM                     | Worker images built with Trivy scan in CI.                                      | Compliance.                                  |

**Pen-test checklist** shipped as Appendix E.


---


### 11.5 Budget & Rate-Limit Guardrails

Peagen exposes metrics for tokens and runtimes but enforcement is left to
infrastructure. The table below lists recommended guard rails at various
levels.

| Level | Mechanism | Example Knobs |
| ----- | --------- | ------------- |
| **Global** | Aggregate `llm_tokens_total` and `worker_runtime_seconds` in Prometheus. Alert when forecast cost exceeds your monthly budget. Optionally share a `TokenBucketRateLimit` via Redis to cap total requests. | `capacity=1_000_000` |
| **Worker** | Set `WORKER_MAX_UPTIME` and `WORKER_IDLE_EXIT`. Instantiate a `TokenBucketRateLimit` per worker if providers enforce request quotas. | `capacity=60`, `refill_rate=1/60` |
| **Task** | Pass `max_tokens` and `timeout_ms` to LLM back-ends. `SubprocessEvaluator` enforces CPU, memory, and wall-clock limits per execute task. | `max_tokens=4096`, `timeout=30s` |
| **Workflow** | Orchestrators track cumulative tokens and wall-clock. Stop when `budget_tokens` or `run_timeout` is reached. | `budget_tokens=50_000` |

These guard rails rely on metrics already produced by the workers and the
`TokenBucketRateLimit` component. Implementers may adapt the policy boundaries
to suit their own infrastructure.


---

### Quick Reference Cheat-Sheet

```bash
# scale up CPU pool manually
docker compose up --scale worker=16

# view live queue & worker counts
redis-cli xlen peagen.tasks
kubectl get pods -l app=peagen-worker

# flush dead-letter to file for triage
peagen queue dlq export > deadletter-2025-06-01.json
```

With these operational controls the task-fabric can run **securely,
observably, and elastically** from a single laptop up to a GPU fleet in
production.
