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

If a phase fails, the guard restores the original methods and the executor rolls back when it owns the transaction. Optional `ON_<PHASE>_ERROR` chains can handle cleanup.

---

This runtime layer is maintained by the core team. Downstream packages should treat it as read‑only and interact only through the public Tigrbl interfaces.

