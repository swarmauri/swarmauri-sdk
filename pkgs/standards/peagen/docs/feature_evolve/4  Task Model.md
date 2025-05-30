## 4 · Task Model

This section specifies the **canonical message format** that flows through the Task-Queue fabric.
All CLI commands, worker handlers, and future automation **MUST** conform to these data structures.

---

### 4.1  `TaskKind` Enumeration

```python
from enum import Enum, auto

class TaskKind(str, Enum):
    RENDER   = "render"     # template expansion only
    MUTATE   = "mutate"     # LLM patch generation
    EXECUTE  = "execute"    # run candidate code, collect metrics
    EVALUATE = "evaluate"   # scorer / evaluator pool
    # (future) LINT, TEST, PUBLISH …
```

*Extensibility rule:* new kinds **MUST** be appended, never re-used.

---

### 4.2  `Task` Dataclass

```python
@dataclass(slots=True)
class Task:
    kind:      TaskKind                 # semantic type
    id:        str                      # UUID-hex, unique
    payload:   dict[str, Any]           # opaque to queue
    requires:  set[str] = field(default_factory=set)  # capability tags
    attempts:  int      = 0             # incremented by queue on retry
    created_at:str      = ts_utc()      # ISO-8601
    schema_v:  int      = 1             # bump on breaking change
```

* **Capability matching** uses `requires`.
  Example: `{"gpu","cuda11","docker"}`.
* **Attempts** enables exponential back-off and dead-letter logic.
* **schema\_v** guards future migrations; workers should error if they encounter an unknown major version.

---

### 4.3  `Result` Dataclass

```python
@dataclass(slots=True)
class Result:
    task_id:   str
    status:    Literal["ok","error","skip"]
    data:      dict[str, Any]        # handler-specific
    created_at:str      = ts_utc()
    attempts:  int      = 1          # attempts that produced this result
```

*Handlers use `status="skip"` to decline after deep inspection (rare).*

---

### 4.4  Capability-Tag Taxonomy

| Tag                  | Meaning                                                | Typical producer                      |
| -------------------- | ------------------------------------------------------ | ------------------------------------- |
| `cpu`                | Generic CPU execution                                  | Render, Mutate, Evaluate, Execute-CPU |
| `llm`                | Network access to LLM provider **and** API key present | Mutate                                |
| `docker`             | Worker able to launch nested `docker run --rm`         | Execute-Docker                        |
| `gpu`                | Host has at least one CUDA-visible GPU                 | Execute-GPU                           |
| `cuda11`, `cuda12`   | Specific driver version                                | Execute-GPU                           |
| `internet`           | Outbound HTTPS allowed                                 | Evaluate (public API)                 |
| `pandas`, `gcc13`, … | Software capability, optional                          | Render data templates, C++ compile    |

*Tag rules*

* lower-case, kebab or snake; no whitespace
* software tags may imply `cpu` unless otherwise noted

---

### 4.5  JSON / MessagePack Encoding

* Wire format: **MessagePack** (`msgspec`) for production; JSON for debugging.
* Key names match dataclass field names.
* Producer must include **all** defined fields; consumer must ignore unknown future fields (forward compatibility).

---

### 4.6  Retry & Dead-Letter Semantics

| Condition                                 | Queue action                                                                 | `attempts` | Remarks                                     |
| ----------------------------------------- | ---------------------------------------------------------------------------- | ---------- | ------------------------------------------- |
| Worker crash, no ACK                      | Message stays in PEL (Redis)                                                 | unchanged  | Spawner calls `XAUTOCLAIM` after 60 s idle. |
| Handler returns `status="error"`          | Orchestrator increments attempts, re-enqueues unless `attempts ≥ MAX_RETRY`. | +1         | Back-off delay doubled each retry.          |
| Attempts exceed `MAX_RETRY` (default = 3) | Message moved to `peagen.dead-letter` stream                                 | final      | CLI displays summary; DevOps investigate.   |

---

### 4.7  Example Serialized Tasks

```jsonc
// MUTATE   (requires LLM + CPU)
{
  "kind": "mutate",
  "id": "a3f8b8d1e8124f90",
  "payload": {
    "parent_src": "def bad_sort(a): ...",
    "entry_fn": "sort",
    "prompt_cfg": {"temperature": 0.7}
  },
  "requires": ["llm", "cpu"],
  "attempts": 0,
  "created_at": "2025-06-01T14:05:23Z",
  "schema_v": 1
}
```

```jsonc
// EXECUTE  (GPU sandbox)
{
  "kind": "execute",
  "id": "c85857d86b274ab1",
  "payload": {
    "child_src": "def sort(a): ...",
    "entry_fn":  "sort",
    "sandbox":   "docker"
  },
  "requires": ["gpu", "cuda11", "docker"],
  "attempts": 1,
  "created_at": "2025-06-01T14:06:02Z",
  "schema_v": 1
}
```

---

### 4.8  Versioning & Compatibility Contract

* `schema_v` increments **major** when a non-optional field changes meaning.
* Producers may only emit the **current** major version.
* Consumers **must** error-out (status `"error"`) if they encounter a higher major version than they support.
* Minor/optional additions do **not** bump `schema_v`; handlers must ignore unknown keys.

---

This task model guarantees:

* **Consistency** – every worker handles the same message envelope.
* **Extensibility** – new TaskKinds, tags, or payload keys can be introduced without queue downtime.
* **Safety** – capability tags and attempts counters enable correct routing and robust retry.
