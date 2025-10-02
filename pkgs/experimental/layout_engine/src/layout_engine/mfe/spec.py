from __future__ import annotations
from dataclasses import dataclass
from typing import Literal
import re

Framework = Literal["svelte","vue","react"]

_ID_RE = re.compile(r"^[a-z][a-z0-9\-]{1,63}$")  # simple, CDN/cache-friendly ids
_EXPOSED_RE = re.compile(r"^(\./)?[A-Za-z0-9_./\-]+$")  # "./App" or "App" or "./lib/App.js"

def validate_id(id: str) -> str:
    if not _ID_RE.match(id):
        raise ValueError(f"invalid remote id '{id}' (lowercase alnum-dash, 2..64)")
    return id

def validate_framework(framework: str) -> Framework:
    if framework not in ("svelte","vue","react"):
        raise ValueError(f"invalid framework '{framework}' (expected svelte|vue|react)")
    return framework  # type: ignore

def validate_entry(entry: str) -> str:
    # allow absolute https/http, root-relative, or relative paths
    s = entry.strip()
    if not (s.startswith("https://") or s.startswith("http://") or s.startswith("/") or s.startswith("./") or s.startswith("../")):
        raise ValueError(f"invalid entry '{entry}' (must be http(s) URL or path)")
    return s

def validate_exposed(exposed: str) -> str:
    if not _EXPOSED_RE.match(exposed):
        raise ValueError(f"invalid exposed module '{exposed}'")
    # normalize to "./X" form
    if not exposed.startswith("./"):
        exposed = "./" + exposed
    return exposed

@dataclass(frozen=True)
class Remote:
    id: str
    framework: Framework
    entry: str            # ESM URL or MF remote entry
    exposed: str          # exposed module (e.g., "./App")
    integrity: str | None = None

    def __post_init__(self):
        validate_id(self.id)
        validate_framework(self.framework)
        validate_entry(self.entry)
        validate_exposed(self.exposed)

    # Import-map entry for this remote
    def as_import(self) -> tuple[str, str]:
        return (self.id, self.entry)
