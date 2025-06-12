"""Canonical SHA-256 hashing utilities for provenance.

All functions return lowercase hexadecimal digests. YAML inputs are
converted to JSON with sorted keys before hashing.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Iterable, Mapping

import yaml

_JSON_OPTS = {"sort_keys": True, "separators": (",", ":")}


def _json_digest(obj: object) -> str:
    text = json.dumps(obj, **_JSON_OPTS)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _yaml_file_digest(path: Path) -> str:
    """Return the canonical digest of a YAML document."""
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return _json_digest(data)


def design_hash(path: Path) -> str:
    """Return the canonical SHA-256 of a design spec."""
    return _yaml_file_digest(path)


def plan_hash(path: Path) -> str:
    """Return the canonical SHA-256 of a plan file."""
    return _yaml_file_digest(path)


def payload_hash(payload: Mapping) -> str:
    """Return the canonical SHA-256 of a payload mapping."""
    return _json_digest(payload)


def revision_hash(parent_rev: str | None, payload_hash: str) -> str:
    """Return the SHA-256 of a revision node."""
    data = {"parent": parent_rev, "payload": payload_hash}
    return _json_digest(data)


def edge_hash(
    parent_rev: str,
    child_payload_hash: str,
    operator_id: str,
    branch_tag: str | None,
) -> str:
    """Return the SHA-256 of an edge descriptor."""
    data = {
        "parent": parent_rev,
        "child": child_payload_hash,
        "operator": operator_id,
        "branch": branch_tag,
    }
    return _json_digest(data)


def fanout_root_hash(edge_hashes: Iterable[str]) -> str:
    """Return the SHA-256 over sorted edge hashes."""
    data = sorted(edge_hashes)
    return _json_digest(data)


def artefact_cid(data: bytes) -> str:
    """Return the SHA-256 of binary artefact data."""
    return hashlib.sha256(data).hexdigest()


def status_hash(rev_hash: str, status: str, timestamp: str) -> str:
    """Return the SHA-256 of a status record."""
    data = {"rev": rev_hash, "status": status, "timestamp": timestamp}
    return _json_digest(data)
