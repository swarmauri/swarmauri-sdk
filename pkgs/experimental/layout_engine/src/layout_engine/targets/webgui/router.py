from __future__ import annotations
from typing import Callable, Mapping, Any

from ...site.spec import SiteSpec, PageSpec
from ...site.default import SiteIndex, build_page_context
from ...manifest.spec import Manifest
from ...manifest.default import manifest_to_json
from ...mfe.default import RemoteRegistry
from .importmap import import_map_json

Html = str


class SiteRouter:
    """Site-aware utilities to generate SSR HTML shells and manifest JSON.

    This class does not depend on any web framework; bind its methods to your routes.
    """

    def __init__(
        self,
        site: SiteSpec,
        page_manifest_fn: Callable[[PageSpec, Mapping[str, Any]], Manifest],
    ):
        self.site = site
        self.page_manifest_fn = page_manifest_fn
        self._index = SiteIndex(site)

    # ---- Shells ----
    def render_shell(
        self,
        page: PageSpec,
        params: Mapping[str, Any] | None = None,
        *,
        lang: str = "en",
        dir: str = "ltr",
        slots_attrs: Mapping[str, Mapping[str, str]] | None = None,
    ) -> Html:
        """Return a minimal SSR HTML containing slot containers.
        Slots are sized/positioned by hydrating clients using the manifest.
        """
        params = params or {}
        slots_attrs = slots_attrs or {}
        head = f"""<meta charset='utf-8'>
<meta name='viewport' content='width=device-width, initial-scale=1'>
<title>{page.title}</title>
<style>
  html,body,#app{{height:100%;margin:0}}
  .slot{{position:relative;min-height:10px}}
</style>"""
        slots_html = []
        for s in page.slots:
            attrs = " ".join(
                f"{k}='{v}'" for k, v in (slots_attrs.get(s.name, {}) or {}).items()
            )
            slots_html.append(f"<div class='slot' data-slot='{s.name}' {attrs}></div>")
        body = f"<div id='app'>{''.join(slots_html)}</div>"
        return f"<!doctype html><html lang='{lang}' dir='{dir}'><head>{head}</head><body>{body}</body></html>"

    # ---- Manifest ----
    def manifest_for(
        self,
        page: PageSpec,
        *,
        query: Mapping[str, Any] | None = None,
        extras: Mapping[str, Any] | None = None,
    ) -> Manifest:
        ctx = build_page_context(
            match=self.site.resolve(page.route)
            or self._index.resolve(page.route)  # local self route
            or self._index.resolve(
                page.route if page.route.startswith("/") else ("/" + page.route)
            ),
            query=query or {},
            extras=extras or {},
        )
        # Allow page_vm as defaults merged into ctx
        cm = dict(ctx)
        cm.update(page.page_vm or {})
        return self.page_manifest_fn(page, cm)

    def manifest_json(
        self,
        page: PageSpec,
        *,
        query: Mapping[str, Any] | None = None,
        extras: Mapping[str, Any] | None = None,
        indent: int | None = None,
    ) -> str:
        m = self.manifest_for(page, query=query, extras=extras)
        return manifest_to_json(m, indent=indent)

    # ---- Path-driven helpers (MPA) ----
    def manifest_for_path(
        self,
        absolute_path: str,
        *,
        query: Mapping[str, Any] | None = None,
        extras: Mapping[str, Any] | None = None,
    ) -> Manifest:
        match = self._index.resolve(absolute_path)
        if not match:
            raise KeyError(f"No page matches path: {absolute_path}")
        ctx = build_page_context(match, query=query or {}, extras=extras or {})
        page = match.page
        cm = dict(ctx)
        cm.update(page.page_vm or {})
        return self.page_manifest_fn(page, cm)

    def manifest_json_for_path(
        self,
        absolute_path: str,
        *,
        query: Mapping[str, Any] | None = None,
        extras: Mapping[str, Any] | None = None,
        indent: int | None = None,
    ) -> str:
        m = self.manifest_for_path(absolute_path, query=query, extras=extras)
        return manifest_to_json(m, indent=indent)

    # ---- Import map ----
    def import_map(
        self, registry: RemoteRegistry, *, include_integrity: bool = True
    ) -> dict:
        return import_map_json(registry, include_integrity=include_integrity)
