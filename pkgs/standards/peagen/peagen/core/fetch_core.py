# peagen/core/fetch_core.py
"""
Pure business-logic for *fetching* a Peagen workspace from one or more
v3 manifests.  No CLI, RPC, or logging dependencies.

Key entry-points
----------------
• fetch_many() – high-level orchestration for N manifests
• fetch_single() – one manifest → workspace
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse, urlunparse

from peagen._utils._template_sets import install_template_sets          # legacy helper
from peagen._utils._source_packages import materialise_packages          # legacy helper
from peagen.plugins.storage_adapters import make_adapter_for_uri          # adapter factory


# ─────────────────────────── low-level helpers ────────────────────────────
def _download_manifest(uri: str) -> Dict[str, Any]:
    """
    Retrieve and parse a manifest JSON from *uri*.

    • Local paths are read directly.
    • Remote URIs are fetched through the storage-adapter designated
      by their `<scheme>://<netloc>/…` prefix.
    """
    if "://" not in uri:  # plain file path
        return json.loads(Path(uri).read_text(encoding="utf-8"))

    p = urlparse(uri)
    if not p.scheme or not p.netloc:
        raise ValueError(f"Invalid manifest URI: {uri!r}")

    # isolate container / bucket URI so the adapter can list+download
    dir_path, key_name = p.path.rsplit("/", 1)
    dir_uri = urlunparse((p.scheme, p.netloc, dir_path, "", "", ""))

    adapter = make_adapter_for_uri(dir_uri)
    with adapter.download(key_name) as fh:               # type: ignore[attr-defined]
        return json.load(fh)


def _materialise_workspace(manifest: Dict[str, Any], dest: Path) -> None:
    """
    Download the *workspace* snapshot referenced by *manifest* into *dest*.
    """
    ws_uri = manifest["workspace_uri"]
    adapter = make_adapter_for_uri(ws_uri)
    prefix = getattr(adapter, "_prefix", "")
    adapter.download_prefix(prefix, dest)                # type: ignore[attr-defined]


# ───────────────────────────── public API ─────────────────────────────────
def fetch_single(
    manifest_uri: str,
    *,
    dest_root: Path,
    install_template_sets_flag: bool = True,
    no_source: bool = False,
) -> Dict[str, Any]:
    """
    Materialise **one** manifest into *dest_root*.

    Returns a dict describing what was done so that callers / handlers
    can aggregate results.
    """
    manifest = _download_manifest(manifest_uri)

    if install_template_sets_flag and manifest.get("template_sets"):
        install_template_sets(manifest["template_sets"])

    if not no_source and manifest.get("source_packages"):
        materialise_packages(
            manifest["source_packages"], workspace=dest_root, upload=False
        )

    _materialise_workspace(manifest, dest_root)

    return {
        "manifest": manifest_uri,
        "processed_template_sets": bool(manifest.get("template_sets")),
        "processed_source_packages": bool(manifest.get("source_packages"))
        and not no_source,
    }


def fetch_many(
    manifest_uris: List[str],
    *,
    out_dir: Optional[Path] = None,
    install_template_sets_flag: bool = True,
    no_source: bool = False,
) -> Dict[str, Any]:
    """
    Orchestrate reconstruction of **multiple** manifests.

    Creates *out_dir* if it does not exist (or a temp dir if omitted)
    and returns a summary payload suitable for JSON-serialisation.
    """
    workspace = (
        out_dir.resolve()
        if out_dir
        else Path(tempfile.mkdtemp(prefix="peagen_ws_")).resolve()
    )
    workspace.mkdir(parents=True, exist_ok=True)

    results = [
        fetch_single(
            m_uri,
            dest_root=workspace,
            install_template_sets_flag=install_template_sets_flag,
            no_source=no_source,
        )
        for m_uri in manifest_uris
    ]

    return {"workspace": str(workspace), "manifests": results}
