## 9 · CLI Surfaces & User Stories

Peagen’s CLI is the **single public interface** for every persona—from an
engineer hacking locally to an Ops engineer running a 100-pod swarm.
All heavy-duty commands eventually delegate to the task-fabric, but users
never need to think about the queue.

```
peagen
├─ render            (deterministic Jinja/templating)
├─ mutate            (one LLM patch, no evaluation)
├─ evolve
│    ├─ step         (one generation: mutate → execute → evaluate)
│    └─ run          (loop step until stop-condition)
└─ worker
     └─ start        (spawn warm-spawner + one-shot workers)
```

> **Global options** (`--config PATH`, `--verbose/-v`, `--dry-run`) come from a
> shared Typer decorator in `cli_common.py`.

---

### 9.1 `peagen render`

| Flag             | Purpose                       | Default   |
| ---------------- | ----------------------------- | --------- |
| `--project`      | Path to project YAML / TOML   | inferred  |
| `--out`          | Destination directory         | `./build` |
| `--queue/--sync` | Enqueue vs blocking local run | `--queue` |
Values fall back to `.peagen.toml` when omitted.

**Example**

```bash
peagen render --project site.yaml --out build/ --sync
```

*Renders synchronously using StubQueue + InlineWorker.*

---

### 9.2 `peagen mutate`

| Flag             | Purpose                    | Default             |
| ---------------- | -------------------------- | ------------------- |
| `--target-file`  | Parent source path         | `bad_sort.py`       |
| `--entry-fn`     | Function to keep stable    | required            |
| `--output`       | Write mutated child here   | `target_mutated.py` |
| `--backend`      | Force specific LLM backend | auto                |
| `--queue/--sync` | Run via queue or inline    | `--queue`           |

Defaults read from `.peagen.toml` when flags omitted.
**Example**

```bash
peagen mutate --target-file bad_sort.py --entry-fn sort --sync
```

*Produces `bad_sort_mutated.py` in same folder.*

---

### 9.3 `peagen evolve step`

| Flag                          | Purpose                            | Default           |
| ----------------------------- | ---------------------------------- | ----------------- |
| `--target-file`, `--entry-fn` | As above                           | infer from config |
| `--selector`                  | Parent selector plugin             | from .toml        |
| `--mutator`                   | Mutator plugin                     | from .toml        |
| `--backend`                   | Execute sandbox tag (`cpu`, `gpu`) | from .toml        |
| `--sync`                      | Run with StubQueue/InlineWorker    | **False**         |

*Returns JSON summary:* best speed, mem, bucket, generation.

---

### 9.4 `peagen evolve run`

| Flag            | Purpose                     | Default                          |
| --------------- | --------------------------- | -------------------------------- |
| `--generations` | Hard cap                    | `[evolve.stop]`                  |
| `--target-ms`   | Speed target for early stop | `[evolve.stop]`                  |
| `--checkpoint`  | Path to save/load EvoDB     | `.peagen/evo_checkpoint.msgpack` |
| `--resume`      | Continue from checkpoint    | False                            |
| `--dashboard`   | Launch live TUI             | False                            |
Defaults read from `.peagen.toml` `[evolve.*]` sections.

**Example (team CI):**

```bash
peagen evolve run --generations 200 --dashboard
```

*Streams progress. Automatically enqueues tasks; requires worker pool.*

---

### 9.5 `peagen worker start`

| Flag / Env                     | Purpose                                | Example             |
| ------------------------------ | -------------------------------------- | ------------------- |
| `--caps` / `WORKER_CAPS`       | Capability tags this worker advertises | `gpu,cuda11,docker` |
| `--plugins` / `WORKER_PLUGINS` | Whitelist of handler class names       | `ExecuteGPUHandler` |
| `--concurrency`                | Parallel tasks (threads/proc)          | `1` (one-shot)      |
| `--warm-pool`                  | Reserved idle pods (only for spawner)  | `2`                 |
| `--exit-after-idle`            | Seconds; self-terminate after idle     | `600`               |

*For local testing:*

```bash
WORKER_CAPS=cpu,docker, llm peagen worker start --concurrency 1
```

---

### 9.6 End-to-End User Stories

| #        | Persona & Goal                                                     | CLI Steps                                                                                                                                 | Expected Outcome                                                          |
| -------- | ------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------- |
| **US-1** | *Backend engineer* wants a quick single improvement to a function. | 1. `peagen mutate --target-file bad_sort.py --entry-fn sort --sync`                                                                       | Creates `bad_sort_mutated.py`; prints diff summary in <2 s.               |
| **US-2** | *Researcher* runs a 50-gen evolution on laptop.                    | 1. `peagen evolve run --generations 50 --sync`                                                                                            | StubQueue handles tasks; best variant saved to `winner.py` in \~5 min.    |
| **US-3** | *DevOps* bursts 32 CPU workers in Docker Compose for a long run.   | 1. `docker compose up -d redis`  2. `docker compose up -d --scale worker=32` 3. `peagen evolve run`                                       | Queue depth falls steadily; Grafana dashboard shows token/s & best-score. |
| **US-4** | *Data-scientist* wants GPU-accelerated execution only.             | 1. `peagen evolve run --backend gpu` 2. Launch GPU worker: `WORKER_CAPS=gpu,cuda11,docker peagen worker start`                            | Execute tasks routed only to GPU worker; Mutate tasks to CPU pool.        |
| **US-5** | *Community contributor* adds a new selector.                       | 1. Publish wheel with entry-point `peagen.parent_selectors.ucb`. 2. User sets `selector="ucb"` in `.peagen.toml`. 3. `peagen evolve run`. | Runner loads new selector without code change; selector’s metrics appear. |

---

### 9.7 Common Patterns Cheat-Sheet

| Need                                  | Command                                                    |
| ------------------------------------- | ---------------------------------------------------------- |
| Local smoke test with no Redis/Docker | `peagen mutate --sync`                                     |
| Resume an interrupted evolution       | `peagen evolve run --resume`                               |
| Drain dead-letter queue               | `peagen queue dlq retry --kind execute`                    |
| Tail live best-speed graph            | `peagen evolve run --dashboard`                            |
| Spawn GPU pool on k8s                 | `peagen worker start (Deployment with WORKER_CAPS=gpu...)` |

These surfaces deliver a **predictable developer UX** while hiding
task-queue complexity, satisfying the product objective of a unified workflow
surface (P-5).
