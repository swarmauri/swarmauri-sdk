## 10 · Configuration Schema (`.peagen.toml`)

A single TOML file in the workspace root governs **all** runtime behaviour.
Loading order = **CLI flags ▶ Environment variables ▶ `.peagen.toml` ▶ Built-in defaults**.

---

### 10.1  Global Sections

| Table               | Key           | Type                                 | Default           | Purpose                                        |
| ------------------- | ------------- | ------------------------------------ | ----------------- | ---------------------------------------------- |
| `[task_queue]`      | `provider`    | `"stub"` \| `"redis"` \| plugin name | `"stub"`          | Selects `TaskQueue` adapter.                   |
|                     | `url`         | string (URI)                         | `""` (stub)       | e.g. `redis://user:pw@host:6379/0`.            |
|                     | `idle_ms`     | int                                  | `60000`           | Idle threshold for orphan reclaim.             |
|                     | `max_retry`   | int                                  | `3`               | Moves to dead-letter after this many attempts. |
| `[result_backend]`  | `provider`    | `"fs"` \| plugin                     | `"fs"`            |                                                |
|                     | `root`        | path                                 | `.peagen/results` | FS backend directory.                          |
|                     | `compress`    | bool                                 | `true`            | Gzip MessagePack files.                        |
| `[worker.defaults]` | `caps`        | csv tags                             | `"cpu"`           | Default `WORKER_CAPS`.                         |
|                     | `concurrency` | int                                  | `1`               | Parallel tasks per pod.                        |
|                     | `warm_pool`   | int                                  | `2`               | Idle pod buffer.                               |
|                     | `max_uptime`  | string (ISO8601 dur)                 | `"4h"`            | Self-recycle.                                  |

---

### 10.2  Mutation Workflow

```toml
[mutate]
mutator       = "patch"           # entry-point
target_file   = "bad_sort.py"
entry_fn      = "sort"
temperature   = 0.7
max_tokens    = 4096
backend       = "auto"            # llm backend or "auto"
```

---

### 10.3  Evolution Workflow

```toml
[evolve]
selector      = "epsilon"
mutator       = "patch"
backend       = "docker"          # execution sandbox tag
entry_fn      = "sort"

[evolve.stop]
max_generations = 200
target_ms       = 3.0
no_improve      = 25

[evolve.archive]
speed_bin_ms = 5
mem_bin_kb   = 32
size_bin_ch  = 40
```

`selector`-specific options nest:

```toml
[selector.epsilon]
eps_init = 0.15
decay    = 0.96
floor    = 0.02
```

---

### 10.4  Evaluation

```toml
[evaluate]
pool  = "default"          # evaluator pool name
metric = "speed_ms"        # future: composite metrics table
```

---

### 10.5  LLM Ensemble

```toml
[llm]
default_backend = "openai"

[[llm.backends]]
name   = "openai"
model  = "gpt-4o-mini"
api_key_env = "OPENAI_API_KEY"
timeout_ms  = 30000
weight = 3        # routing probability weight

[[llm.backends]]
name   = "groq"
model  = "mixtral-8x22b"
api_key_env = "GROQ_API_KEY"
weight = 1
```

Routing probability `P(backend) = weight / Σweights` unless CLI `--backend` overrides.

---

### 10.6  Templates

```toml
[templates]
search_path = ["./my_custom_templates"]
```

Peagen looks here **before** its built-ins when rendering `agent_evolve.j2`.

---

### 10.7  Secrets & Env Overrides

*Any key can be overridden with `PEAGEN__<TABLE>__<KEY>` env variable*
(e.g. `PEAGEN__TASK_QUEUE__URL=redis://…`).
Secret tokens **must** be passed via env or secret manager, never stored in TOML.

---

### 10.8  Example Minimal File

```toml
# .peagen.toml — laptop defaults
[task_queue]
provider = "stub"

[mutate]
target_file = "bad_sort.py"
entry_fn    = "sort"

[evolve]
selector       = "epsilon"
backend        = "docker"
entry_fn       = "sort"
[evolve.stop]
max_generations = 100
```

Running `peagen evolve run` on such a project works offline.
Switching to Redis production is a 4-line edit in `[task_queue]`.

---

### 10.9  Loading Utility

```python
from peagen.util.toml_loader import load_peagen_toml
cfg = load_peagen_toml(Path("."))
queue_url = cfg["task_queue"]["url"]         # typed objects
```

`load_peagen_toml()` merges env overrides and validates against an internal
pydantic schema, raising `ConfigError` on misuse.

---

This schema provides **predictable knobs** for users, a stable contract for
dev-tools, and clear extension points for future brokers, handlers or metrics.
