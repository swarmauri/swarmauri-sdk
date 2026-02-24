#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SVELTE_RUNTIME_SRC="$REPO_ROOT/pkgs/experimental/swarmakit/libs/layout-engine-svelte"
SWARMAKIT_SVELTE_SRC="$REPO_ROOT/pkgs/experimental/swarmakit/libs/svelte"
RUNTIME_DEST="$REPO_ROOT/pkgs/experimental/layout_engine_atoms/src/layout_engine_atoms/runtime/svelte/assets"

echo "Building layout-engine Svelte runtime bundle…"

pushd "$SVELTE_RUNTIME_SRC" >/dev/null
pnpm install --no-frozen-lockfile
pnpm build
popd >/dev/null

echo "Building SwarmaKit Svelte component bundle…"
pushd "$SWARMAKIT_SVELTE_SRC" >/dev/null
pnpm install --no-frozen-lockfile
pnpm build
popd >/dev/null

mkdir -p "$RUNTIME_DEST/layout-engine-svelte" "$RUNTIME_DEST/swarma-svelte"

cp "$SVELTE_RUNTIME_SRC/dist/index.js" "$RUNTIME_DEST/layout-engine-svelte/index.js"
cp "$SVELTE_RUNTIME_SRC/dist/style.css" "$RUNTIME_DEST/layout-engine-svelte/style.css"
cp "$SVELTE_RUNTIME_SRC/dist/bootstrap/mpa-bootstrap.js" \
   "$RUNTIME_DEST/layout-engine-svelte/mpa-bootstrap.js"

cp "$SWARMAKIT_SVELTE_SRC/dist/index.esm.js" "$RUNTIME_DEST/swarma-svelte/svelte.js"
cp "$SWARMAKIT_SVELTE_SRC/dist/style.css" "$RUNTIME_DEST/swarma-svelte/style.css"

echo "Svelte runtime assets updated under $RUNTIME_DEST"
