from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Dict, Mapping, Pattern, Tuple

from pydantic import BaseModel, Field

# ---- utilities ----


def normalize_base_path(p: str) -> str:
    if not p:
        return "/"
    if not p.startswith("/"):
        p = "/" + p
    if len(p) > 1 and p.endswith("/"):
        p = p[:-1]
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
                raise ValueError(
                    "Wildcard '*' is only allowed once at the end of the route"
                )
            regex_parts.append("(?P<rest>.*)")
            param_names.append("rest")
            wildcard_used = True
            continue
        if seg.startswith(":"):
            name = seg[1:]
            if not name or not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", name):
                raise ValueError(f"Invalid route param name: {seg}")
            regex_parts.append(rf"(?P<{name}>[^/]+)")
            param_names.append(name)
        else:
            regex_parts.append(re.escape(seg))
    regex = "^/" + "/".join(regex_parts) + "/?$"
    return re.compile(regex), tuple(param_names)


# ---- specs ----


class SlotSpec(BaseModel):
    name: str
    role: str
    remote: str | None = None


class PageSpec(BaseModel):
    id: str
    route: str
    title: str
    slots: Tuple[SlotSpec, ...] = ()
    page_vm: Mapping[str, Any] = Field(default_factory=dict)
    meta: Mapping[str, Any] = Field(default_factory=dict)

    # derived (lazy): compiled pattern and params
    def match(self, path: str) -> dict[str, str] | None:
        pat, _ = compile_route_pattern(self.route)
        m = pat.match(path)
        if not m:
            return None
        return {k: v for k, v in m.groupdict().items() if v is not None}


class SiteSpec(BaseModel):
    base_path: str = "/"
    pages: Tuple[PageSpec, ...] = ()


@dataclass(frozen=True)
class RouteMatch:
    page: "PageSpec"
    params: Dict[str, str]
    path: str
