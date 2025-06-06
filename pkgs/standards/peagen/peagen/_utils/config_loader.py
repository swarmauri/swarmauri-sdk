"""
peagen._utils.config_loader
===========================

Utilities for loading and merging Peagen configuration layers.

Layers (lowest → highest priority)
----------------------------------
1. Built-in defaults              (peagen.defaults.CONFIG)
2. Host-wide .peagen.toml         (from disk *or* in-memory text)
3. Batch-level overrides          (--batch-cfg passed once per CLI invocation)
4. CLI / Sub-command flags        (parsed inside the specific command)
5. Per-task overrides             (added by the handler before calling core)
"""

from __future__ import annotations
from pathlib import Path
from typing import Any, Dict
from copy import deepcopy
import toml

import peagen.defaults as builtins


# ────────────────────────────────────────────────────────────────────────────
# 1. Low-level loader
# ────────────────────────────────────────────────────────────────────────────
def load_peagen_toml(
    path: str | Path = ".peagen.toml"
) -> Dict[str, Any]:
    """
    Read *path* as TOML and return a dict.  If the file is missing and
    ``required`` is False, return an **empty dict** instead.

    Gateways / workers should call with ``required=True`` so they fail fast
    when the config file is absent.
    """
    p = Path(path)
    if not p.exists():
        if required:
            raise FileNotFoundError(f"{p!s} is required on this host")
        return {}
    return toml.loads(p.read_text())


# ─────────────────────────────── .peagen override ────────────────────────────
def _effective_cfg(cfg_path: Optional[Path]) -> Dict[str, Any]:
    """
    Load the TOML file *only if* the caller supplied an explicit
    `--config/-c` path.  
    • If the path is a directory, look for `.peagen.toml` inside it.  
    • If no path is given, we return an **empty dict** (no implicit fallback).
    """
    if cfg_path is None:                       # ← no config provided
        return {}

    p = Path(cfg_path)
    if not p.exists():
        if required:
            raise FileNotFoundError(f"{p!s} is required on this host")
        return {}

    if cfg_path.is_dir():                      # allow “-c ./some/dir”
        cfg_path = cfg_path / ".peagen.toml"

    # require_file=True so we fail fast on a bad path
    return resolve_cfg(toml_path=cfg_path)


# ────────────────────────────────────────────────────────────────────────────
# 3. Public merge helper – replaces the old _resolve_cfg
# ────────────────────────────────────────────────────────────────────────────
def resolve_cfg(*, toml_text: dict | str | None = None,
                toml_path: str = ".peagen.toml") -> dict:
    """
    FINAL MERGE ORDER  ➜  built-ins  <  host file  <  task override
    """
    cfg = deepcopy(builtins.CONFIG)                              # ① built-ins

    cfg = _merge(cfg, load_peagen_toml(toml_path))  # ② merge host cfg
    if toml_text:                                                   # ③ per-task
        override = toml.loads(toml_text) if isinstance(toml_text, str) else toml_text
        cfg = _merge(cfg, override)
    return cfg


def _merge(a: dict, b: dict) -> dict:
    """Recursively merge b into (a copy of) a and return the copy."""
    out = deepcopy(a)
    for k, v in b.items():
        if k in out and isinstance(out[k], dict) and isinstance(v, dict):
            out[k] = _merge(out[k], v)           # nested dict → recurse
        else:
            out[k] = deepcopy(v)                 # overwrite / add
    return out