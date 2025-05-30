## 12 · Performance Targets & Benchmark Plan

The following targets translate product KPIs (Section 2) into **numerical
accept-criteria** and outline the automated benchmarks that will gate every
PR and release.

| ID       | Metric                                                                                | Target v0.9                   | Target v1.0 | Measurement Harness       |
| -------- | ------------------------------------------------------------------------------------- | ----------------------------- | ----------- | ------------------------- |
| **PT-1** | *Time-to-best* on **bad\_sort** baseline (single host, 32 CPU workers, Redis Streams) | ≤ 5 min                       | ≤ 2 min     | `benchmarks/bad_sort.py`  |
| **PT-2** | *Worker cold-start latency* (container start → task claimed)                          | ≤ 3 s on CPU, ≤ 10 s on GPU   | ≤ 2 s / 8 s | `bench_hatchery.py`       |
| **PT-3** | *Queue throughput* (Redis Streams)                                                    | ≥ 5 000 tasks / min sustained | ≥ 10 000    | `bench_queue_rate.py`     |
| **PT-4** | *Token efficiency* – tokens per 1 % speed-gain (bad\_sort)                            | ≤ 40 K                        | ≤ 25 K      | gathers from Prom metrics |
| **PT-5** | *Idle cost* (billable pod-seconds during 12 h idle window)                            | < 0.5 h CPU, 0 h GPU          | 0 h CPU/GPU | `bench_idle_cost.py`      |
| **PT-6** | *Crash recovery* – orphan task reclaimed & completed                                  | < 90 s                        | < 60 s      | `bench_fault_inject.py`   |
| **PT-7** | *Determinism* – re-run with same seed reproduces best speed within tolerance          | ± 1 %                         | ± 0.5 %     | `bench_replay.py`         |

---

### 12.1  Benchmark Environments

| Name            | Hardware                                  | Purpose                        |
| --------------- | ----------------------------------------- | ------------------------------ |
| **DEV-STUB**    | Developer laptop; StubQueue; InlineWorker | CI unit & smoke tests          |
| **CPU-FARM-32** | 1× AWS c6a.8xlarge (32 vCPU) + Redis 7    | Main throughput & time-to-best |
| **GPU-FARM-1**  | 1× A100 40 GB + Docker + nvidia runtime   | GPU executor latency           |
| **K8S-SWARM**   | 3× c6a.4xlarge + HPA & Redis Cluster      | Autoscaling & idle-cost        |

Terraform manifests supplied under `/infra/benchmark/`.

---

### 12.2  Harness Components

* **`bench_runner.py`** — grabs `.peagen.toml`, spins workers (Compose or k8s), launches requested CLI command, records timestamps via Prometheus query API.
* **`bench_report.ipynb`** — Jupyter notebook turns raw `.jsonl` metrics into markdown summary & plots.
* **GitHub Action** `benchmark.yml` — nightly run on CPU-FARM-32; fails if any PT target regresses beyond 5 %.

---

### 12.3  Test Workloads

| Workload           | Description                              | CLI Invocation                        |
| ------------------ | ---------------------------------------- | ------------------------------------- |
| **bad\_sort**      | 100-line O(n²) sorter; objective = speed | `peagen evolve run --generations 120` |
| **slow\_shortest** | Dijkstra in pure Python dicts            | `peagen evolve run` w/ graph profile  |
| **render\_site**   | 200 Jinja templates + 5 MB CSV           | `peagen render`                       |

All workloads live in `benchmarks/artifacts/`.

---

### 12.4  Acceptance Gates

* **PR gate**: run DEV-STUB smoke test; ensure unit coverage ≥ 85 %.
* **Nightly gate**: run full PT-1..PT-4 on CPU-FARM-32; fail build on regression.
* **Release gate**: run all PT-1..PT-7 on all four environments; generate PDF report and attach to release artifact.

---

### 12.5  Data Retention

* Raw Prometheus snapshots stored 30 days in `s3://peagen-bench`.
* Notebook HTML reports kept indefinitely under GitHub Releases “Benchmark report”.

---

### 12.6  Owner & Cadence

| Deliverable                | Owner               | Frequency          |
| -------------------------- | ------------------- | ------------------ |
| Maintain benchmark harness | Core-Infra          | ongoing            |
| Review nightly regressions | Release Engineering | daily stand-up     |
| Produce release report     | Performance WG      | each minor release |

---

Meeting these performance targets ensures Peagen not only works but **delights end users** with rapid iterations, predictable costs, and provable robustness.
