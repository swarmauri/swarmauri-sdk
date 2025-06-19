"""Custom reference names and helpers for :class:`~peagen.plugins.vcs.git_vcs.GitVCS`."""

PEAGEN_REFS_PREFIX = "refs/pea"

FACTOR_REF = f"{PEAGEN_REFS_PREFIX}/factor"
RUN_REF = f"{PEAGEN_REFS_PREFIX}/run"
ANALYSIS_REF = f"{PEAGEN_REFS_PREFIX}/analysis"
EVO_REF = f"{PEAGEN_REFS_PREFIX}/evo"
PROMOTED_REF = f"{PEAGEN_REFS_PREFIX}/promoted"


def pea_ref(kind: str, *parts: str) -> str:
    """Return ``refs/pea/<kind>/<parts...>``."""
    suffix = "/".join(part.strip("/") for part in parts)
    return f"{PEAGEN_REFS_PREFIX}/{kind}/{suffix}" if suffix else f"{PEAGEN_REFS_PREFIX}/{kind}"

