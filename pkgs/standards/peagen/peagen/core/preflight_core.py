"""preflight_core
================

Business logic for preflight environment checks.

This module validates Peagen configuration, ensures a Git mirror
repository exists and generates/registers an SSH deploy key when needed.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from peagen.core.validate_core import validate_config
from peagen.plugins.vcs import GitVCS
from peagen.core.keys_core import create_keypair, upload_public_key

DEFAULT_GATEWAY = "http://localhost:8000/rpc"


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def ensure_mirror(path: Path, url: str) -> Dict[str, Any]:
    """Ensure ``path`` is a Git mirror of ``url``."""
    vcs = GitVCS.ensure_repo(path, remote_url=url)
    return {"mirror": str(path), "remote": url, "exists": vcs.has_remote()}


def ensure_deploy_key(name: str, gateway_url: str = DEFAULT_GATEWAY) -> Dict[str, Any]:
    """Generate and register an SSH deploy key."""
    paths = create_keypair()
    upload_public_key(gateway_url=gateway_url)
    return {"key_name": name, "private": paths["private"], "public": paths["public"]}


# ---------------------------------------------------------------------------
# public API
# ---------------------------------------------------------------------------


def preflight(
    repo_url: str,
    mirror_path: Path,
    *,
    cfg_path: Optional[Path] = None,
    gateway_url: str = DEFAULT_GATEWAY,
) -> Dict[str, Any]:
    """Run all preflight checks."""
    cfg_result = validate_config(cfg_path)
    mirror_result = ensure_mirror(mirror_path, repo_url)
    key_result = ensure_deploy_key("deploy-key", gateway_url)
    return {
        "config": cfg_result,
        "mirror": mirror_result,
        "deploy_key": key_result,
    }


__all__ = ["preflight", "ensure_mirror", "ensure_deploy_key"]
