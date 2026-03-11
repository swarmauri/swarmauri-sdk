# Runtime Execution Module (v3)

> **Maintainer-only:** This module is internal to the SDK. Downstream users **must not** modify or rely on it directly.

The runtime executor coordinates Tigrbl operations through a fixed set of **phase chains**. Each phase has a list of steps built by the kernel and is executed with strict phase-bound database capabilities.

## Kernel Architecture Form

Tigrbl's runtime kernel follows a **compiled spec form with predicate-gated
phase-chain execution**. It is not imperative request handling and not purely
declarative configuration.

The kernel form is:

`Spec → Normalization → Compilation → KernelPlan → PhaseChain execution over GwRawEnvelope`

1. `AppSpec` is normalized into `NormalizedSpec`.
2. `NormalizedSpec` is compiled once into a deterministic `KernelPlan`.
3. `Executor(plan).invoke(env)` executes ordered phase chains over a raw
   transport envelope.

At runtime, the executor behaves like a compiled plan engine:

- compile once and cache the plan,
- run ingress chain,
- resolve an operation key by indexed protocol lookup,
- run operation chain,
- run egress chain.

Dispatch is index-based (`proto_indices[proto][route_key] -> opkey`), not
router traversal. Operation metadata (`opmeta[opkey]`) drives deterministic
execution.

### Canonical KernelPlan Shape

Conceptually, the compiled plan contains:

- `proto_indices` – protocol-to-route hash maps for O(1) dispatch,
- `opmeta` – operation metadata keyed by operation key,
- `ingress_chain` – ordered atoms before operation execution,
- `op_chains` – per-operation ordered atoms,
- `egress_chain` – ordered atoms after operation execution.

Atoms are small execution units with optional predicates. Predicate checks gate
execution without introducing heuristic branching in the executor.

### Classification

In systems terms, the runtime kernel is a deterministic, compiled,
phase-oriented dispatch engine derived from normalized application
specification. This gives:

- compile-once / execute-many behavior,
- deterministic and inspectable plans,
- protocol abstraction over a raw envelope,
- phase-level security and diagnostics injection,
- consistent phase ordering.

## Phase Chains

Phase chains map phase names to ordered handler lists. The executor runs the phases in the sequence below:

1. `PRE_TX_BEGIN` – pre-transaction checks.
2. `START_TX` – open a new transaction (system-only).
3. `PRE_HANDLER` – request validation and setup.
4. `HANDLER` – core operation logic.
5. `POST_HANDLER` – post-processing while still in the transaction.
6. `PRE_COMMIT` – final checks before committing.
7. `END_TX` – commit and close the transaction.
8. `POST_COMMIT` – steps after commit.
9. `POST_RESPONSE` – fire-and-forget side effects.

## Step Kinds

The kernel labels every piece of work so it can be ordered predictably:

- **secdeps** – security dependencies that run before any other steps. Downstream
  applications configure these to enforce authentication or authorization.
- **deps** – general dependencies resolved ahead of handlers. These are also
  provided downstream.
- **sys** – system steps shipped with Tigrbl to coordinate core behavior. They
  are maintained by project maintainers.
- **atoms** – built-in runtime units such as schema collectors or wire
  serializers. Maintainers own these components.
- **hooks** – user-supplied handlers that attach to anchors within phases.

Downstream consumers configure `secdeps`, `deps`, and `hooks`, while `sys` and
`atom` steps are maintained by the Tigrbl maintainers.


## Step Precedence

When the kernel assembles an operation it flattens several step kinds into a
single execution plan. They run in the following precedence:

1. Security dependencies (`secdeps`)
2. General dependencies (`deps`)
3. System steps (`sys`) such as transaction begin, handler dispatch, and commit
4. Runtime atoms (`atoms`)
5. Hooks (`hooks`)

System steps appear only on the `START_TX`, `HANDLER`, and `END_TX` anchors. Within
each anchor, atoms execute before hooks and any remaining ties are resolved by
anchor-specific preferences.

## Atom Domains

Atoms are grouped into domain-specific registries so the kernel can inject them
at the correct stage of the lifecycle. Each domain focuses on a different slice
of request or response processing:

- **wire** – builds inbound data, validates it, and prepares outbound payloads at
  the field level.
- **schema** – collects request and response schema definitions for models.
- **resolve** – assembles derived values or generates paired inputs before they
  are flushed.
- **storage** – converts field specifications into storage-layer instructions.
- **emit** – surfaces runtime metadata such as aliases or extras for downstream
  consumers.
- **out** – mutates data after handlers run, for example masking fields before
  serialization.
- **response** – negotiates content types and renders the final HTTP response or
  template.
- **refresh** – triggers post-commit refreshes like demand-driven reloads.

Domains differ by the moment they run and the guarantees they provide. A `wire`
atom transforms raw request values before validation, whereas a `response` atom
operates after the transaction is committed to shape the returned payload. The
kernel uses the pair `(domain, subject)` to register and inject atoms into phase
chains.

## PhaseDb

For every phase, the kernel injects a builtin phase-entry step that binds
`ctx.db` to a `PhaseDb` capability adapter. The raw DB handle is stored as
`ctx._raw_db` and is not the public execution surface.

`PhaseDb` enforces phase legality structurally:

- `flush()` is allowed only in phases whose capability table permits it
- `commit()` is allowed only in phases whose capability table permits it
- `commit()` additionally requires transaction ownership when configured
- `refresh()` is phase-gated explicitly

The runtime no longer monkey-patches DB methods. It stamps `ctx.phase` and
`ctx.owns_tx`; the first builtin phase step materializes the restricted DB
surface for that phase.

| Phase | Flush | Commit | Notes |
|-------|-------|--------|-------|
| PRE_TX_BEGIN | ❌ | ❌ | no database writes |
| START_TX | ❌ | ❌ | transaction opening |
| PRE_HANDLER | ✅ | ❌ | writes allowed, commit blocked |
| HANDLER | ✅ | ❌ | writes allowed, commit blocked |
| POST_HANDLER | ✅ | ❌ | writes allowed, commit blocked |
| PRE_COMMIT | ❌ | ❌ | freeze writes before commit |
| END_TX | ✅ | ✅ | commit allowed only if runtime owns the transaction |
| POST_COMMIT | ✅ | ❌ | post-commit writes without commit |
| POST_RESPONSE | ❌ | ❌ | background work, no writes |

### Transaction Boundaries

`start_tx` is a system step that opens a new database transaction when
no transaction is active and marks the runtime as its owner. While this
phase runs, both `session.flush` and `session.commit` are blocked. After a
transaction is started, phases such as `PRE_HANDLER`, `HANDLER`, and
`POST_HANDLER` allow flushes so SQL statements can be issued while the
commit remains deferred. The `end_tx` step executes during the `END_TX`
phase, performing a final flush and committing the transaction if the
runtime owns it. Once this phase completes, subsequent phases can rebind `ctx.db` with their
own capability surface.

If a phase fails, the executor rolls back when it owns the transaction. Optional `ON_<PHASE>_ERROR` chains can handle cleanup.

---

This runtime layer is maintained by the core team. Downstream packages should treat it as read‑only and interact only through the public Tigrbl interfaces.
