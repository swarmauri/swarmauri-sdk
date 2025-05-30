## 13 · Roll-Out / Migration Plan

This phased plan upgrades every existing Peagen workspace from the
**mono/dev** branch to the new task-fabric without downtime, while giving all
teams a clear fallback at each checkpoint.

| Mile- | Target Date     | Deployable Increment                                                                                | Success Criteria                                                      | Rollback                                                    |
| ----- | --------------- | --------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------- | ----------------------------------------------------------- |
| **A** | -1 week         | **StubQueue & InlineWorker** merged; `peagen mutate --sync` replaces `peagen process`.              | Unit-tests pass in CI; legacy commands aliased.                       | Revert to tag `pre-fabric` (no schema change).              |
| **B** | 0 week (0.2.0 GA) | **Redis Streams adapter, one-shot workers, warm-spawner** behind feature flag `PEAGEN_QUEUE=redis`. | CPU-farm benchmark PT-1 ≤ 5 min; nightlies green.                     | Env var `PEAGEN_QUEUE=stub` restores inline path.           |
| **C** | +2 weeks        | **Capability tags, GPU Execute handler**; Kubernetes HPA manifests.                                 | GPU benchmark PT-2 latency ≤ 10 s; autoscaler charts stable 24 h.     | Scale HPA to 0, switch back to CPU pool.                    |
| **D** | +4 weeks        | **Selectors & Mutators pluggable**, EvoDB checkpoint resume.                                        | Third-party demo wheel runs with no code mods; replay test PT-7 ±1 %. | Flip `[evolve] selector="legacy"` in TOML.                  |
| **E** | +6 weeks        | **Cost & metric dashboards, DLQ tooling, idle-to-zero**; deprecate old commands.                    | Idle cost PT-5 < 0.5 h; Ops runbook signed off.                       | Disable warm-spawner - deploy always-on pool for emergency. |

---

### 13.2 Backward-Compatibility Matrix

| Existing Artifact                         | Status after GA                                   | Migration Aid                                          |
| ----------------------------------------- | ------------------------------------------------- | ------------------------------------------------------ |
| `peagen process`                          | **Alias** to `peagen render`. Warns once per run. | Remove in 0.4.0.                                        |
| CI scripts that call `--workers` flag     | Still valid (maps to StubQueue concurrency).      | Docs update.                                           |
| Old `.peagen.toml` with no `[task_queue]` | Auto-defaults to `provider="stub"`.               | `peagen config upgrade` inserts minimal queue section. |

---

### 13.3 Step-by-Step Upgrade for a Team

1. **Dev Branch**

   ```bash
   pip install --upgrade peagen==0.2.0
   peagen mutate --sync   # smoke test with StubQueue
   ```
2. **Add queue section**

   ```toml
   [task_queue]
   provider = "redis"
   url      = "redis://localhost:6379/0"
   ```
3. **Launch local worker**

   ```bash
   redis-server --daemonize yes
   peagen worker start &
   peagen evolve step   # should enqueue + drain
   ```
4. **CI Update** – add Redis service to pipeline; replace `peagen process` job with `peagen render`.
5. **Staging Cluster**

   * Apply `k8s/spawner-cpu.yaml`.
   * Export Prometheus dashboard; verify metrics 24 h.
6. **Prod Cut-Over** – flip `PEAGEN_QUEUE=redis://redis.prod:6379/0` via secret manager; deploy GPU spawner if needed.
7. **Monitor** – Alerting matrix Section 11.3; rollback env var to `stub` if queue lag > threshold.

---

### 13.4 Training & Documentation

* 30-min kickoff video for engineers (CLI changes, new flags).
* Confluence page “Writing a TaskHandler in 10 minutes”.
* Ops runbook: Redis HA, spawner HPA, DLQ triage.
* Slack #peagen-fabric for on-call week one.

---

### 13.5 Risk Mitigation

| Risk                      | Mitigation / Flag                                                                                    |
| ------------------------- | ---------------------------------------------------------------------------------------------------- |
| Redis outage stalls queue | `PEAGEN_QUEUE=stub` feature flag – CLI falls back to inline execution.                               |
| Worker image bug          | Blue-green roll-out; old image tag kept 14 days.                                                     |
| Token cost spike          | Dashboard + alert `llm_tokens_total` (Section 11).                                                   |
| Perf regression           | Nightly benchmarks fail build; release blocked.                                                      |
| Compatibility break       | `schema_v` bump in Task/Result; workers refuse higher major – orchestrator feature-flag to old path. |

The staged milestones, reversible flags, and clear ownership ensure a **safe,
incremental migration** to the new scalable task-fabric while meeting the
product’s performance and cost objectives.
