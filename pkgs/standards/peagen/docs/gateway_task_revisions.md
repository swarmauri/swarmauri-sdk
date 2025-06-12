# Gateway Task Revisions

The Peagen gateway now records every task update in an append-only
`task_revision` table. Each revision stores the base64 encoded payload,
its SHA-256 hash, the parent revision hash, and a computed `rev_hash` of
`SHA256(parent_rev_hash‖payload_hash)`.

Submitting a DOE specification also validates the provided
`design_hash` and `plan_hash` values. These hashes are upserted into the
`manifest` table so duplicate submissions reuse the same manifest row.

Clients patch tasks by including `parent_rev_hash` in the JSON-RPC
params. The gateway rejects mismatched hashes with
`PeagenHashMismatchError`.
