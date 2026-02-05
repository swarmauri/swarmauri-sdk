from __future__ import annotations

import warnings

from fastapi import APIRouter, Body, Depends, FastAPI, HTTPException, Path, Security

warnings.warn(
    "tigrbl.deps.fastapi is deprecated; use tigrbl.deps.stdapi instead.",
    DeprecationWarning,
    stacklevel=2,
)

Router = APIRouter

# ── Public Exports ───────────────────────────────────────────────────────
__all__ = [
    "APIRouter",
    "Router",
    "FastAPI",
    "Security",
    "Depends",
    "Path",
    "Body",
    "HTTPException",
]
