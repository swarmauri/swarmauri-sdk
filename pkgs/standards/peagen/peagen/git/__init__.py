"""Git reference helpers used by peagen workflows."""

from __future__ import annotations

# Base prefix for all peagen-managed refs
PEAGEN_REFS_PREFIX = "refs/pea"

# Common ref namespaces
FACTOR_REF = f"{PEAGEN_REFS_PREFIX}/factor"
RUN_REF = f"{PEAGEN_REFS_PREFIX}/run"
ANALYSIS_REF = f"{PEAGEN_REFS_PREFIX}/analysis"
EVO_REF = f"{PEAGEN_REFS_PREFIX}/evo"
PROMOTED_REF = f"{PEAGEN_REFS_PREFIX}/promoted"


def pea_ref(*parts: str) -> str:
    """Return a fully qualified reference under :data:`PEAGEN_REFS_PREFIX`."""
    if not parts:
        raise ValueError("at least one ref component required")
    joined = "/".join(part.strip("/") for part in parts)
    return f"{PEAGEN_REFS_PREFIX}/{joined}"

__all__ = [
    "PEAGEN_REFS_PREFIX",
    "FACTOR_REF",
    "RUN_REF",
    "ANALYSIS_REF",
    "EVO_REF",
    "PROMOTED_REF",
    "pea_ref",
]
