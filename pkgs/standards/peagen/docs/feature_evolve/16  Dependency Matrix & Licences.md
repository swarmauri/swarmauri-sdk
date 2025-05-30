## 16 · Dependency Matrix & Licences

| Layer                 | Package (PyPI / System)         | Version Pin (≥)  | Licence    | Purpose                                      | Notes                          |
| --------------------- | ------------------------------- | ---------------- | ---------- | -------------------------------------------- | ------------------------------ |
| **Core runtime**      | `typer`                         | 0.12             | MIT        | CLI façade                                   | Sub-dependency of `rich`.      |
|                       | `rich`                          | 13.7             | MIT        | Pretty TUI / logging.                        |                                |
|                       | `msgspec`                       | 0.18             | Apache-2.0 | Ultra-fast MessagePack (Task/Result ser-de). | No GPL code.                   |
|                       | `redis` (`redis-py`)            | 5.0              | BSD-3      | Queue adapter (Streams).                     | TLS supported.                 |
|                       | `docker` (`docker-py`)          | 7.0              | Apache-2.0 | Spawn nested sandboxes (execute).            | Optional on CPU-only installs. |
|                       | `jinja2`                        | 3.1              | BSD-3      | Render templates.                            |                                |
|                       | `pydantic`                      | 2.7              | MIT        | Config validation.                           |                                |
|                       | `prometheus-client`             | 0.19             | Apache-2.0 | Metrics exposition.                          |                                |
|                       | `opentelemetry-api`             | 1.25             | Apache-2.0 | Distributed traces (optional).               |                                |
| **LLM ensemble**      | `openai`                        | 1.25             | Apache-2.0 | OpenAI backend.                              | Instal-on-demand.              |
|                       | `groq-sdk`                      | 0.5              | MIT        | Groq backend.                                |                                |
|                       | `llama-cpp-python`              | 0.2              | MIT        | Local GGUF backend.                          | Heavy; wheels per-platform.    |
| **Dev / CI**          | `pytest`, `hypothesis`          | 8.2, 6.100       | MIT        | Unit + fuzz tests.                           | Not in prod wheels.            |
|                       | `ruff`                          | 0.4              | MIT        | Lint & format.                               |                                |
|                       | `mypy`                          | 1.10             | MIT        | Static typing.                               |                                |
|                       | `pytest-cov`                    | 4.2              | MIT        | Coverage report.                             |                                |
| **Security scanning** | `bandit`                        | 1.7              | Apache-2.0 | Python vuln scan.                            | Dev only.                      |
| **Containers**        | `ghcr.io/swarmauri/eval-python` | tag = commit-sha | Apache-2.0 | Base image for Execute-Docker handler.       | Alpine, non-root.              |
|                       | `redis:7-alpine`                | 7.x              | BSD-3      | Broker.                                      | Official image.                |

\### Licence Summary

* **Peagen core code** ➜ **Apache-2.0** (same as Swarmauri-SDK).
* All **runtime dependencies** are Apache-2.0, MIT, or BSD-3—compatible with Apache.
* **No GPL / AGPL transitive licences** are introduced in the default install path.
* Docker base images use OSI-approved licences (Alpine MIT, Debian GPL-compatible but runtime-only).

\### Compliance Workflow

1. **`make license-scan`** runs `pip-licenses --format=csv` + Trivy SBOM; fails CI if GPL appears.
2. Third-party plugin wheels must declare licence in `pyproject.toml`; plugin index shows badge.
3. Release artefact bundles `THIRD_PARTY_NOTICE.md`—auto-generated from the matrix above.
4. Docker images include `/licenses/*` copies to satisfy container distribution requirements.

\### Optional / External
Dependencies listed as *optional extras* (`pip install peagen[gpu,llm]`) are:

* `torch` (+ CUDA) → BSD (optional for local GGUF GPU accelerate).
* Cloud-specific SDKs (AWS SQS, GCP Pub/Sub) each follow their respective Apache/MIT licences; they are loaded only if the matching `TaskQueue` plugin is installed.

This matrix gives legal, security, and package-management teams a clear view of what’s shipped, why it’s needed, and how it is licensed.
