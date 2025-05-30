## 7 · TaskHandlers

TaskHandlers are the **plug-and-play execution units** inside every worker.
They interpret a `Task`’s payload, perform the domain work, and return a
`Result`.  The queue layer is completely agnostic to what a handler does.

---

### 7.1  Core Interface

```python
# peagen/handlers/base.py
class TaskHandler(ComponentBase, Protocol):
    KIND:      TaskKind              # the TaskKind it serves
    PROVIDES:  set[str]              # capability tags it fulfils

    def dispatch(self, task: Task) -> bool: ...
        # quick, side-effect-free filter; may inspect payload fields

    def handle(self, task: Task) -> Result: ...
        # MUST be idempotent, raise only if unrecoverable
```

* Handlers are discovered through the entry-point group
  `peagen.task_handlers`.
* **Capability rule:** A worker will invoke a handler only if
  `task.requires ⊆ handler.PROVIDES ⊆ WORKER_CAPS`.

---

### 7.2  Built-in Handlers (0.2.0)

| Handler (module)                            | KIND       | PROVIDES                    | Key Responsibilities                                                                                             |
| ------------------------------------------- | ---------- | --------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| **RenderHandler** (`render_handler.py`)     | `RENDER`   | `{"cpu"}`                   | • Jinja render / file write<br>• Deterministic, no LLM                                                           |
| **PatchMutatorHandler** (`mutate_patch.py`) | `MUTATE`   | `{"llm","cpu"}`             | • Build evolve-prompt via `PromptSampler`<br>• Call `LLMEnsemble.generate`<br>• Apply diff, emit **ExecuteTask** |
| **ExecuteDockerHandler** (`exec_docker.py`) | `EXECUTE`  | `{"docker","cpu"}`          | • Bind-mount child\_src into eval image<br>• Capture speed & memory JSON                                         |
| **ExecuteGPUHandler** (`exec_gpu.py`)       | `EXECUTE`  | `{"docker","gpu","cuda11"}` | • Same as CPU but passes `--gpus 1`                                                                              |
| **EvaluateHandler** (`eval_handler.py`)     | `EVALUATE` | `{"cpu"}`                   | • Run `EvaluatorPool`, compute score                                                                             |

All internal tasks (`evolve step`) can complete with only these five handlers.

---

### 7.3  Plugin Registration Example

`pyproject.toml` of an external wheel:

```toml
[project.entry-points."peagen.task_handlers"]
cpp_exec = "my_pkg.cpp_exec:ExecuteCppHandler"
```

`ExecuteCppHandler.PROVIDES = {"gcc13","cpu","docker"}` – tasks that require
`{"gcc13"}` will now find a match if the worker image advertises that tag.

---

### 7.4  Selective Loading in Worker

```python
if PLUGINS and handler.__class__.__name__ not in PLUGINS:
    continue            # allow-list filter
```

`WORKER_PLUGINS="MutateHandler,RenderHandler"` (env) restricts a worker to
those two handlers, even if others are present in the image.

---

### 7.5  Error & Retry Contract

| Handler outcome                      | `Result.status`                         | Queue action                                         |
| ------------------------------------ | --------------------------------------- | ---------------------------------------------------- |
| Success                              | `"ok"`                                  | ACK task; orchestrator proceeds                      |
| Transient (e.g. LLM 503)             | `"error"` **and** `data.retryable=True` | Queue increments `attempts`, re-queues with back-off |
| Permanent (bad patch, compile error) | `"error"` & `retryable=False`           | Orchestrator moves to DLQ immediately                |
| Decline / capability mis-match       | `"skip"`                                | Task remains un-ACK’ed; other worker will claim      |

Handlers **MUST** never crash the worker; raise only if restart is safer.

---

### 7.6  Metrics Emitted by Handler

| Name                       | Type      | Labels               | Meaning                     |
| -------------------------- | --------- | -------------------- | --------------------------- |
| `handler_duration_seconds` | histogram | `handler`, `status`  | Wall-clock per task         |
| `handler_fail_total`       | counter   | `handler`, `reason`  | Number of `"error"` results |
| `llm_tokens_total`         | counter   | `handler`, `backend` | Emitted only by mutators    |

Metrics integrate with the `ComponentBase` logger; Prometheus scrape path
`/metrics` is exposed by each worker. Logging behaviour can be tuned via
`HandlerBase` and `FormatterBase` implementations, and handlers may optionally
annotate traces using `SimpleTracer` to correlate with metrics.

---

### 7.7  Sample Handler Code – EvaluateHandler

```python
# peagen/handlers/eval_handler.py
class EvaluateHandler(TaskHandler):
    KIND      = TaskKind.EVALUATE
    PROVIDES  = {"cpu"}

    def dispatch(self, task: Task) -> bool:
        return task.kind == self.KIND

    def handle(self, task: Task) -> Result:
        ws_uri  = task.payload["workspace_uri"]
        pool_id = task.payload.get("pool", "default")
        try:
            score = EvaluatorPool.from_name(pool_id).evaluate_workspace(ws_uri)
            return Result(task.id, "ok", {"score": score})
        except Exception as e:
            return Result(task.id, "error", {"msg": str(e), "retryable": False})
```

---

### 7.8  Handler Development Checklist (for contributors)

1. **Declare** `KIND` and full `PROVIDES` set.
2. **Pure-function** logic inside `handle`; side-effects after success only.
3. Use `ComponentBase.logger` for debug lines.
4. **Unit-test**: feed sample `Task`, assert `Result.status`.
5. Document any new capability tags in Cap-tag taxonomy appendix.

Following these rules guarantees reliable routing, safe retries, and observability across the entire fabric.
