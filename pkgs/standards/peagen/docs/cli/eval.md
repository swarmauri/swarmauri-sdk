# `peagen eval`

`peagen eval` runs EvaluatorPool benchmarks against a workspace produced by `peagen program fetch`.

```console
peagen eval WORKSPACE_URI [PROGRAM_GLOB] [OPTIONS]
```

Options mirror those described in IP-0004. Pools can be referenced using a
dotted path, a `module:Class` path, or an entry-point name defined under the new
`evaluator_pools` group.

The command writes an `eval_manifest.json` next to other artefacts under `.peagen/`.
