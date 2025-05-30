## 15 · Contribution & Extension Guidelines

These rules keep the Peagen ecosystem **stable, discoverable, and safe** while
still allowing rapid third-party innovation.

---

### 15.1  Adding a New *TaskHandler* (e.g., `ExecuteRustHandler`)

| Step                       | Detail                                                                                                                                                                                                                                                                                   |
| -------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1 – Create module          | `src/my_pkg/rust_exec.py`                                                                                                                                                                                                                                                                |
| 2 – Subclass `TaskHandler` | `python\nclass ExecuteRustHandler(TaskHandler):\n    KIND = TaskKind.EXECUTE\n    PROVIDES = {\"cpu\",\"docker\",\"rust\"}\n    def dispatch(self, task):\n        return task.kind == self.KIND and task.payload.get(\"lang\") == \"rust\"\n    def handle(self, task):\n        ...\n` |
| 3 – Register entry-point   | `toml\n[project.entry-points.\"peagen.task_handlers\"]\nrust_exec = \"my_pkg.rust_exec:ExecuteRustHandler\"\n`                                                                                                                                                                           |
| 4 – Capability doc         | Add `rust` line to Cap-Tag appendix in README.                                                                                                                                                                                                                                           |
| 5 – Tests                  | Unit-test happy path + error path; integration stub test.                                                                                                                                                                                                                                |
| 6 – Metrics                | Emit `handler_duration_seconds`, `handler_fail_total`.                                                                                                                                                                                                                                   |
| 7 – License                | Apache-2.0 or MIT; include NOTICE if bundling third-party code.                                                                                                                                                                                                                          |

**Validation**

```bash
pip install -e .[dev]
peagen mutate --sync  # should auto-discover new handler if requires match
```

---

### 15.2  Adding an LLM Backend Adapter

1. **Implement** `class OpenRouterBackend(LLMBackend)` with `.generate()`.
2. **Register** under `peagen.llm_backends`.
3. Export metrics `llm_tokens_total{backend="openrouter"}`.
4. Document required env var (`OPENROUTER_API_KEY`).
5. Provide `tests/test_openrouter_backend.py` with `vcr.py` cassettes.

---

### 15.3  Adding a Parent Selector

1. Subclass `ParentSelector`.
2. Register via `peagen.parent_selectors`.
3. Provide `[selector.<name>]` config docs.
4. Unit-test selection distribution and feedback adaptation.

---

### 15.4  Coding Standards

| Tool           | Enforcement                              |
| -------------- | ---------------------------------------- |
| **Typing**     | `mypy --strict` (all public funcs typed) |
| **Linting**    | `ruff check` (PEP-8 + project rules)     |
| **Formatting** | `ruff format` (auto on pre-commit)       |
| **Security**   | `bandit -r src` – fix high/medium        |

*CI will fail PRs that violate any of the above.*

---

### 15.5  Project Layout Conventions

```
my_pkg/
 ├─ src/my_pkg/
 │    ├─ __init__.py
 │    ├─ handlers/...
 │    └─ selectors/...
 ├─ tests/
 ├─ pyproject.toml     # includes entry-points
 └─ README.md          # capability tags, usage
```

---

### 15.6  Versioning & Compatibility

* Follow **semver**.
* Breaking change to `Task` or `Result` schema requires `schema_v += 1`.
* Entry-point names must remain stable; deprecate via warning for ≥1 minor
  version before removal.

---

### 15.7  Documentation Checklist (PR Template)

* [ ] Added/updated docstring for every public class & function.
* [ ] Added section to `docs/plugins.md`.
* [ ] Described new capability tags.
* [ ] Changelog line in `CHANGELOG.md`.

---

### 15.8  Publishing to PyPI

1. Include `entry-points` in `pyproject.toml`.
2. Tag release `vX.Y.Z`.
3. Upload with `twine upload dist/*`.
4. Announce in **#peagen-plugins** Slack channel.

---

### 15.9  Security Review for Handlers

| Requirement                                                 | Rationale             |
| ----------------------------------------------------------- | --------------------- |
| No network calls unless capability tag `internet` declared. | Prevent data leakage. |
| Validate all untrusted input (e.g., diff length ≤ 200 KB).  | Resource safety.      |
| Cleanup temp files (`with tempfile.TemporaryDirectory()`).  | Disk quota.           |
| Use `subprocess.run(..., check=True, timeout=…)`.           | Avoid hangs.          |

Handlers failing security review will be blocked from the official plugin index.

---

### 15.10  Support & Governance

*Core maintainers* review and merge PRs within **72 h**.
Discussions: GitHub issues → “Enhancement” label.
Large proposals need an **ADR** (Architecture Decision Record).

These guidelines ensure every extension—internal or community—stays
compatible, performant, and secure, sustaining a healthy Peagen ecosystem.
