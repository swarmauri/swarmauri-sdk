# Operational Guide

This page collects day‑2 practices for running Peagen in production. It distills
Section&nbsp;11 of the internal brief and the relevant appendices.

## Autoscaling Recipes

Peagen workers can run on a laptop farm or a full Kubernetes cluster. Example
manifests live under `infra/examples/`.

| Environment | Scale Up | Idle Scale-Down | Notes |
|-------------|---------|-----------------|-------|
| **Docker Compose** | `watch-queue.py` polls `queue_pending_total` every 30&nbsp;s and runs `docker compose up --scale worker=<n>` | Same script scales to zero after five idle minutes | Simple and works without cloud services |
| **Kubernetes** | `Deployment/peagen-worker` with an `HorizontalPodAutoscaler` using external metric `redis_queue_pending{stream="peagen.tasks"}` | `minReplicas: 0` with a `scaleDown.stabilizationWindowSeconds: 300` | Keep two idle pods ahead via the spawner warm pool |
| **AWS Fargate** | CloudWatch alarm on pending count triggers Step&nbsp;Function to start tasks | A second alarm sets desired count to zero | Serverless pay‑per‑second |
| **systemd** | `systemd-run --unit=peagen-worker@$(uuidgen)` from cron when queue depth is high | `StopWhenUnneeded=yes` in the unit file | Runs even on bare metal |

## Fault‑Tolerance Runbook

Workers acknowledge tasks only when processing succeeds. If a container dies
mid‑task, the spawner periodically calls `XAUTOCLAIM` to reclaim the orphan. Use
`peagen queue dlq export` to inspect dead‑letter messages for repeated failures.

1. **Crash Recovery** – check `worker_exit_reason_total{reason="error"}` and
   `queue_pending_idle_max_seconds` for growing values. The spawner should
   requeue within 60&nbsp;s by default.
2. **Dead‑Letter Queue** – export stuck tasks using:
   ```bash
   peagen queue dlq export > dlq.json
   ```
   Triage and requeue once the underlying issue is fixed.

## Monitoring

Metrics follow the observability matrix in the brief. Key signals include:

- `queue_pending_total` and `worker_exit_reason_total`
- `handler_fail_total` and `result_backend_fail_total`
- `llm_tokens_total` per backend

Dashboards typically contain a *Main* view for queue and worker health and a
*Cost* board tracking token spend. See Appendix&nbsp;B for the full metric list.

## Security Hardening

Container images run with `no-new-privileges`, a read‑only root filesystem and
seccomp `runtime/default`. Workers mount no secrets except environment variables
injected by the orchestrator. Limit resources with `--pids-limit` and memory
quotas. The [pen‑test checklist](../../pkgs/standards/peagen/docs/feature_evolve/18%20%20Appendices.md#appendix-e--security--pen-test-checklist)
requires:

- `bandit -r src` with zero high findings
- `make trivy-scan` yielding zero critical vulnerabilities
- Chaos test: kill a worker mid-task and verify requeue

## Budget & Rate‑Limit Controls

Guardrails rely on `llm_tokens_total` and `worker_runtime_seconds` metrics.
Configure a shared `TokenBucketRateLimit` in Redis or pass
`--budget-tokens`/`--run-timeout` flags per workflow. Example:

```toml
[evolve]
backend = "gpu"
[evolve.limits]
budget_tokens = 50000
run_timeout = 3600
```

## Example Commands

```bash
# Deploy reference Redis on Kubernetes
kubectl apply -f infra/examples/redis-broker.yaml

# Verify worker UID is non-root
./infra/examples/verify-nonroot.sh
```

