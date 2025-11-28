"""FastAPI demo using the packaged layout engine Vue runtime."""

from __future__ import annotations

from fastapi import FastAPI, Request

from layout_engine_atoms.runtime.vue import mount_layout_app
from .manifest import build_manifest_dict

app = FastAPI(title="Layout Engine Atoms Demo")

_MANIFEST_CACHE = build_manifest_dict()


def _manifest_builder(_: Request):
    return _MANIFEST_CACHE


mount_layout_app(
    app,
    manifest_builder=_manifest_builder,
    base_path="/",
    title="Layout Engine × SwarmaKit",
)
