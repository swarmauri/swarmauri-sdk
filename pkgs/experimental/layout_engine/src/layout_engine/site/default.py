from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Mapping, Any, Iterable, Dict, Tuple, Optional

from .spec import SiteSpec, PageSpec, RouteMatch, compile_route_pattern, normalize_base_path
from ..manifest.spec import Manifest

# ---- DI: Manifest builder binding ----

def bind_page_builder(build_fn: Callable[[PageSpec, Mapping[str, Any]], Manifest]) -> Callable[[PageSpec, Mapping[str, Any]], Manifest]:
    """Return the given function; placeholder for dependency injection hooks."""
    return build_fn

# ---- Site index / resolver ----

@dataclass(slots=True)
class _Entry:
    page: PageSpec
    regex: Any     # compiled Pattern[str]
    params: Tuple[str, ...]
    route: str

class SiteIndex:
    """Pre-compiled resolver for SiteSpec.

    - Compiles each PageSpec.route to a regex.
    - Resolves absolute paths by stripping SiteSpec.base_path, then matching.
    """
    def __init__(self, site: SiteSpec):
        self.base = normalize_base_path(site.base_path)
        entries: list[_Entry] = []
        for p in site.pages:
            regex, names = compile_route_pattern(p.route)
            entries.append(_Entry(page=p, regex=regex, params=names, route=p.route))
        self._entries = entries

    def resolve(self, absolute_path: str) -> RouteMatch | None:
        rel = absolute_path
        if self.base != "/" and absolute_path.startswith(self.base):
            rel = absolute_path[len(self.base):] or "/"
        for e in self._entries:
            m = e.regex.match(rel)
            if m:
                params = {k: v for k, v in m.groupdict().items() if v is not None}
                return RouteMatch(page=e.page, params=params, absolute_path=absolute_path, relative_path=rel)
        return None

def resolve_path(site: SiteSpec, absolute_path: str) -> RouteMatch | None:
    return SiteIndex(site).resolve(absolute_path)

# ---- Validation ----

def validate_site(site: SiteSpec) -> None:
    seen_ids: set[str] = set()
    seen_routes: set[str] = set()
    if site.base_path != normalize_base_path(site.base_path):
        raise ValueError("base_path is not normalized")
    for p in site.pages:
        if p.id in seen_ids:
            raise ValueError(f"duplicate page id: {p.id}")
        seen_ids.add(p.id)
        if not p.route.startswith("/"):
            raise ValueError(f"page.route must start with '/': {p.id}")
        # compile to ensure patterns are valid
        compile_route_pattern(p.route)
        if p.route in seen_routes:
            # Allow colliding routes if they are different by pattern? We keep it strict.
            raise ValueError(f"duplicate page route: {p.route}")
        seen_routes.add(p.route)
        for s in p.slots:
            if not s.name:
                raise ValueError(f"slot name must be non-empty on page {p.id}")

# ---- Context assembly ----

def build_page_context(match: RouteMatch, *, query: Mapping[str, Any] | None = None, extras: Mapping[str, Any] | None = None) -> dict:
    """Assemble a minimal context dict for manifest/page rendering.

    Contains:
      - page: PageSpec (as object)
      - route: { absolute, relative, params, query }
      - slots: [ {name, role, remote} ... ]
      - meta:  page.meta
    """
    q = dict(query or {})
    ctx = {
        "page": match.page,
        "route": {
            "absolute": match.absolute_path,
            "relative": match.relative_path,
            "params": dict(match.params),
            "query": q,
        },
        "slots": [{"name": s.name, "role": s.role, "remote": s.remote} for s in match.page.slots],
        "meta": dict(match.page.meta),
    }
    if extras:
        ctx.update(extras)
    return ctx
