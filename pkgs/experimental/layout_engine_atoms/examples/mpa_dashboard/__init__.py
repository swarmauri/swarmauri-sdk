"""Interactive multi-page dashboard demo built on layout_engine_atoms."""

from __future__ import annotations

__all__ = ["DEFAULT_PAGE_ID", "available_pages", "build_manifest", "resolve_page_by_route"]

from .manifests import DEFAULT_PAGE_ID, available_pages, build_manifest, resolve_page_by_route
