## 2 · Product Objectives

| ID      | Objective                                                                                                              | Why Users Care                                                                             | Success KPI                                                                                                                 | Release Target |
| ------- | ---------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------- | -------------- |
| **P-1** | **Elastic Throughput** – Automatically scale from laptop-mode (stub queue) to 50 parallel workers without CLI changes. | Teams evolving code bases shouldn’t wait hours for results; capacity should follow demand. | *Time-to-best Variant* on public “bad\_sort” benchmark ≤ **5 min** with 32 CPU workers; ≤ **30 min** with single-host stub. | v0.9 GA        |
| **P-2** | **Zero-Idle Cost** – Workers spin down to zero when queue empty.                                                       | Cloud bills stay flat for inactive projects; on-prem clusters free resources.              | Billable container-hours during 12 h idle window < **0.5 h**.                                                               | v0.9 GA        |
| **P-3** | **Fresh-Environment Execution** – Every task runs in a single-use sandbox.                                             | Eliminates state bleed, flaky tests, and security risk from LLM-generated code.            | No task cross-contamination detected in stress test (hash of `/tmp` & env diff).                                            | v0.9 GA        |
| **P-4** | **Pluggable Innovation Layer** – Selectors, Mutators, Executors, and LLM back-ends are installable via entry-points.   | Research & community extend Peagen without PRs to core repo.                               | “Hello-World” third-party mutator wheel installs & runs in < **10 min** following docs.                                     | v1.0           |
| **P-5** | **Unified Workflow Surface** – All heavy operations (`render`, `mutate`, `evolve`) share one task fabric.              | Single mental model for users; infra team maintains one queue.                             | 100 % of CLI benchmarks pass when executed via queue (no direct mode).                                                      | v0.9 GA        |
| **P-6** | **Deterministic & Reproducible** – Any generation can be replayed given checkpoint + seeds.                            | Debugging and academic comparison require reproducibility.                                 | SHA-replay test reproduces best variant speed within **±1 %**.                                                              | v1.1           |
| **P-7** | **Observability & Budget Guardrails**                                                                                  | PMs need to track token spend and performance; ops must see queue health.                  | Dashboard shows: token/s, pending tasks, best-score graph; alerts fire < 2 min after threshold.                             | v0.9 GA        |
| **P-8** | **Local-Dev First**                                                                                                    | Engineers can run everything without Redis/Docker.                                         | `peagen mutate --sync` succeeds on fresh clone with no docker or redis installed.                                           | v0.9 GA        |

### Supported User-Facing Workflows

1. **Render** – deterministic template expansion (`peagen render`)
2. **Mutate (no eval)** – single LLM patch round (`peagen mutate`)
3. **Evolve Step** – one generation with evaluation (`peagen evolve step`)
4. **Evolve Run** – full search until stop condition (`peagen evolve run`)
5. **Worker Ops** – start capability-scoped worker pools (`peagen worker start`)

### Assumptions & Constraints

* Target runtime: CPython 3.10+; Docker ≥ 24; Redis ≥ 7.0 (Streams).
* GPU tasks require hosts with CUDA 11+ and `nvidia-container-runtime`.
* Max simultaneous workers per workspace: 256 (soft queue limit).
* Budget guardrails compute worst-case token spend using input counts and `max_tokens` (multiplied by file count for `render`) so users know the potential cost before a run begins.

These objectives align engineering deliverables with tangible end-user value and provide clear acceptance criteria for the initial release and subsequent milestones.
