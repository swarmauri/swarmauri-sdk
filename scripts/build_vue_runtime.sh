#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CLIENT_DIR="$REPO_ROOT/pkgs/experimental/layout_engine_atoms/src/layout_engine_atoms/runtime/vue/client"

echo "Building layout-engine Vue runtime bundle (requires Node/npm)…"

pushd "$CLIENT_DIR" >/dev/null
npm install
npm run build:prod
popd >/dev/null

echo "Bundle written to $CLIENT_DIR/dist"
