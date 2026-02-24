# Runtime-owned Routing Contract (No Dispatcher, No Pre-parsing)

This document defines the minimum runtime contract needed to execute requests
strictly through the kernel phase chain, without relying on REST/RPC dispatcher
pre-resolution.

## Objective

- `App.__call__` accepts ASGI3 `scope, receive, send`.
- The runtime receives a `GwRawEnvelope` and owns parse → route → execute → emit.
- Route atoms select `OpKey/OpMeta` at runtime.
- Egress atoms emit over `raw.send`.

## Canonical envelope and context inputs

The runtime entrypoint should always provide:

- `ctx.raw.scope`
- `ctx.raw.receive`
- `ctx.raw.send`

Ingress atoms should derive canonical request fields used by route and handler
atoms:

- `ctx.method`
- `ctx.path`
- `ctx.headers`
- `ctx.query`
- `ctx.body_bytes` (or equivalent stream handle)
- `ctx.proto`

## Route resolution target artifacts

At route completion, runtime atoms should set:

- `ctx.op_key`
- `ctx.op_meta`
- `ctx.path_params`
- `ctx.binding` (if policies are available)
- `ctx.plan` (or equivalent selected chain metadata)

## Anchor-by-anchor minimum write contract

The table below maps each canonical route lifecycle anchor to minimum fields
that should be written to `ctx` for runtime-owned dispatch.

| Anchor | Minimum write(s) |
|---|---|
| `ingress.ctx.init` | initialize `ctx.raw`, `ctx.temp`, request scratch fields |
| `ingress.ctx.attach_compiled` | attach compiled artifacts (route index/trie, op metadata map, plan cache) |
| `ingress.metrics.start` | set request start timestamp/trace id |
| `ingress.method.extract` | write `ctx.method` from `ctx.raw.scope["method"]` |
| `ingress.path.extract` | write `ctx.path` from `ctx.raw.scope["path"]` |
| `ingress.headers.parse` | write normalized `ctx.headers` |
| `ingress.query.parse` | write parsed `ctx.query` |
| `ingress.body.read` | consume ASGI `receive()` frames; write `ctx.body_bytes` |
| `ingress.body.peek` | write lightweight body metadata (size/content-type hints) |
| `route.protocol.detect` | write `ctx.proto` from ASGI scope type/protocol |
| `route.binding.match` | match protocol/method/path tokens against compiled index; write candidate binding/op key |
| `route.rpc.envelope.parse` | if RPC envelope, parse method/params/id into normalized fields |
| `route.rpc.method.match` | resolve RPC method to `ctx.op_key` when relevant |
| `route.op.resolve` | write final `ctx.op_key` and `ctx.op_meta` |
| `route.path_params.extract` | write `ctx.path_params` from match captures |
| `route.params.normalize` | merge/coerce path/query/body parameters for handler input |
| `route.payload.select` | write selected inbound payload object for validation/handler |
| `route.binding.policy.apply` | write effective `ctx.binding` policy result |
| `route.plan.select` | write selected execution chain metadata in `ctx.plan` |
| `route.ctx.finalize` | freeze route-time context needed by downstream phases |

## Execution model

Two valid runtime models exist:

1. **Single plan + runtime gating**: execute one full chain and no-op irrelevant atoms.
2. **Per-op compiled plan cache**: resolve `ctx.op_key`, then execute the op-specific
   chain.

For strict runtime-owned routing with minimal overhead, prefer per-op plan cache.

## Complexity expectations

Let `T` be request token count and `S` be selected chain step count.

- Route match (trie/index): `O(T)` expected.
- `OpKey -> OpMeta`: `O(1)`.
- `OpKey -> PhaseChain`: `O(1)`.
- Runtime atom execution: `O(S)`.

Per-request runtime overhead (excluding handler/storage): `O(T + S)`.
