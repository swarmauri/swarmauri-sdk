## 1 · Executive Summary

*(Peagen Task-Fabric & Evolution Engine — Technical Requirements Brief)*

### 1.1 Purpose of this Document

* Provide a **single source of truth** for everyone who will design, build, deploy or sell the next-generation Peagen runtime.
* Translate the high-level product goal—*“speed-up AI code generation and evaluation while cutting idle cost to zero”*—into **actionable engineering requirements**.
* Define the **interfaces, responsibilities, and success metrics** for all new components: TaskQueue, Workers, Handlers, Selectors, Mutators, LLM Ensemble, Prompt templates, and EvoDB.

### 1.2 Scope & Non-Scope

| In Scope                                                                                                                                                                                                                                                                                                                                                                                                                                                     | Out of Scope                                                                                                                                                                                                                                                                                               |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| - Refactor existing `peagen process` into `peagen render`, `peagen mutate`, `peagen evolve step/run`. <br>- Design & implement **task-queue fabric** (Stub & Redis Streams adapters). <br>- **Capability-matched, one-shot workers + warm-spawner** model. <br>- Core plugin interfaces (TaskHandler, ParentSelector, Mutator, Executor). <br>- EvoDB (MAP-Elites) & adaptive selector feedback. <br>- Prometheus / OTLP metrics, health, autoscaling hooks. | - Full UI/dashboard (will be tackled by Dev-X team). <br>- Production Kubernetes manifests for every cloud; one reference manifest is enough. <br>- Enterprise SSO, RBAC—handled by platform security later. <br>- Alternate brokers (RabbitMQ, SQS) and result stores beyond FS/S3—road-mapped, not 0.2.0. |

---

**Key Take-away:**
This document’s remainder drills from high-level objectives (Section 2) down to implementation specifics (Sections 3-15).  Once approved, it becomes the contractual reference for initial release *Peagen 0.2.0* and all follow-up work streams.
