from __future__ import annotations
from dataclasses import dataclass, field
from typing import Mapping, Any, Tuple, Pattern, Dict, Optional
import re

# ---- utilities ----

def normalize_base_path(p: str) -> str:
    if not p: return "/"
    if not p.startswith("/"): p = "/" + p
    if len(p) > 1 and p.endswith("/"): p = p[:-1]
    return p

def compile_route_pattern(route: str) -> tuple[Pattern[str], tuple[str, ...]]:
    """Compile a route like '/reports/:id' to a regex with named groups.

    Supported:
      - Named segments: ':name' -> (?P<name>[^/]+)
      - Wildcard tail:  '*'     -> (?P<rest>.*)  (single wildcard allowed at the end)
      - Optional trailing slash is accepted.
    """
    if not route.startswith("/"):
        route = "/" + route
    segs = route.strip().split("/")
    regex_parts = []
    param_names: list[str] = []
    wildcard_used = False
    for idx, seg in enumerate(segs):
        if seg == "":
            continue
        if seg == "*":
            if idx != len(segs) - 1 or wildcard_used:
                raise ValueError("Wildcard '*' is only allowed once at the end of the route")
            regex_parts.append("(?P<rest>.*)")
            param_names.append("rest")
            wildcard_used = True
            continue
        if seg.startswith(":"):
            name = seg[1:]
            if not name or not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", name):
                raise ValueError(f"Invalid route param name: {seg}")
            regex_parts.append(fr"(?P<{name}>[^/]+)")
            param_names.append(name)
        else:
            regex_parts.append(re.escape(seg))
    regex = "^/" + "/".join(regex_parts) + "/?$"
    return re.compile(regex), tuple(param_names)

# ---- specs ----

@dataclass(frozen=True)
class SlotSpec:
    name: str
    role: str
    remote: str | None = None

@dataclass(frozen=True)
class PageSpec:
    id: str
    route: str
    title: str
    slots: Tuple[SlotSpec, ...] = ()
    page_vm: Mapping[str, Any] = field(default_factory=dict)
    meta: Mapping[str, Any] = field(default_factory=dict)

    # derived (lazy): compiled pattern and params
    def match(self, path: str) -> dict[str, str] | None:
        pat, _ = compile_route_pattern(self.route)
        m = pat.match(path)
        if not m: return None
        return {k: v for k, v in m.groupdict().items() if v is not None}

@dataclass(frozen=True)
class SiteSpec:
    base_path: str = "/"
    pages: Tuple[PageSpec, ...] = ()

    def __post_init__(self):
        object.__setattr__(self, "base_path", normalize_base_path(self.base_path))

    def routes(self) -> tuple[str, ...]:
        return tuple(p.route for p in self.pages)

    def resolve(self, path: str) -> "RouteMatch | None":
        """Resolve a path to (page, params) after stripping base_path."""
        root = normalize_base_path(self.base_path)
        # strip base prefix
        if root != "/" and path.startswith(root):
            rel = path[len(root):] or "/"
        else:
            rel = path
        for p in self.pages:
            params = p.match(rel)
            if params is not None:
                return RouteMatch(page=p, params=params, absolute_path=path, relative_path=rel)
        return None

@dataclass(frozen=True)
class RouteMatch:
    page: PageSpec
    params: Dict[str, str]
    absolute_path: str
    relative_path: str
