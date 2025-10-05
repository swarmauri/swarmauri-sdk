"""Site model: routes/pages/slots and resolution utilities.

This module defines:
  - SlotSpec, PageSpec, SiteSpec (pure data)
  - Route compilation and matching
  - SiteIndex for fast resolution
  - Helpers for building per-page contexts
"""
from .spec import SlotSpec, PageSpec, SiteSpec, RouteMatch, compile_route_pattern, normalize_base_path
from .shortcuts import slot, page, site
from .default import SiteIndex, resolve_path, validate_site, build_page_context, bind_page_builder

__all__ = [
    "SlotSpec","PageSpec","SiteSpec","RouteMatch",
    "compile_route_pattern","normalize_base_path",
    "slot","page","site",
    "SiteIndex","resolve_path","validate_site","build_page_context","bind_page_builder",
]
