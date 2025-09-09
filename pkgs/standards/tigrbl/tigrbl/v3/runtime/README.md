# Runtime Execution Module (v3)

> **Maintainer-only:** This module is internal to the SDK. Downstream users **must not** modify or rely on it directly.

The runtime executor coordinates Tigrbl operations through a fixed set of **phase chains**. Each phase has a list of steps built by the kernel and is executed under strict database guards.

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

## DB Guards

For every phase the executor installs database guards that monkey‑patch
`commit` and `flush` on the session. Guards enforce which operations are
allowed and ensure only the owning transaction may commit.

The guard installer swaps these methods with stubs that raise
`RuntimeError` when a disallowed operation is attempted. Each phase passes
flags describing its policy:

- `allow_flush` – permit calls to `session.flush`.
- `allow_commit` – permit calls to `session.commit`.
- `require_owned_tx_for_commit` – when `True`, block commits if the
  executor did not open the transaction.

The installer returns a handle that restores the original methods once the
phase finishes so restrictions do not leak across phases. A companion
helper triggers a rollback if the runtime owns the transaction and a phase
raises an error.

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
runtime owns it. Once this phase completes, guards restore the original
session methods.

If a phase fails, the guard restores the original methods and the executor rolls back when it owns the transaction. Optional `ON_<PHASE>_ERROR` chains can handle cleanup.

---

This runtime layer is maintained by the core team. Downstream packages should treat it as read‑only and interact only through the public Tigrbl interfaces.

