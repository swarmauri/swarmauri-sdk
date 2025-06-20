# Patch Workflow

This guide explains how Peagen resolves artifacts and applies patches when processing a Design of Experiments (DoE).

Peagen applies patches in three phases:

1. **Resolve** – fetch the base artifact for each level via `artifactRef` or `uriTemplate`.
2. **Perturb** – optionally clone and tweak artifacts using the `perturbations` list.
3. **Overlay** – merge the level's `patchRef` so manual changes override RNG tweaks.

## Stage 1 – Resolve

The controller turns every URI into a concrete file:

```
artifactRef, targetRef, or the uriTemplate from a factorSet → git+…#commit@path, llm://provider/model, s3://…, http://…, cid://…
Result = base blob (JSON/YAML/binary) + its CID
```

## Stage 2 – Apply Level Patch

```text
Patch at factor level  patchRef (and patchKind)  If the level has its own patch, the engine applies it after perturbations so the level wins over RNG tweaks.
```

## Field Reference

```
Field       Level where it appears    Purpose
artifactRef individual level objects  Direct pointer to one starting blob (config file, model, etc.).
targetRef   less common—used when patching another file  Sometimes you want patch ≠ target (e.g. kubectl strategic-merge against live YAML fetched at run-time).
uriTemplate in factorSet  generates many artifactRef values automatically  Each row in the Cartesian product fills the template placeholders to create unique URIs.
```

## Patch Sources

```
How you declare it              What it looks like                        Best when…
Inline level patch              patchRef: "patches/sgd_lr_0.01.jsonpatch" patchKind: json-patch  One file → one level  Hand-crafted overrides or CI-generated JSON Merge/Patch blobs.
Perturbations list              perturbations[*].patchRef + repeats       Vectorised cloning  Want N randomised copies of the same base blob.
Mutator patch pool              patchRefPool: git+…@patches/pool/  patchSpace: patch_spaces/hyper.yaml  Ongoing stochastic exploration  Evolutionary phase; sample new tweaks each epoch
```

## Supported patchKinds

```
Value        Engine does…                                  Notes
git          runs git apply in a scratch work-tree         For plain-text (code, Dockerfile).
json-patch   RFC 6902 op list                              Precise adds / removes / replaces.
json-merge   RFC 7386 overlay                              Whole sub-trees replaced; null deletes.
(others)     any plugin name                               The engine loads it via entry-points; schema allows free strings.
```
