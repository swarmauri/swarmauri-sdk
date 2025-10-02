from __future__ import annotations
from .spec import SiteSpec, PageSpec, SlotSpec, normalize_base_path

def slot(name: str, role: str, remote: str | None = None) -> SlotSpec:
    return SlotSpec(name=name, role=role, remote=remote)

def page(id: str, route: str, title: str, *, slots: tuple[SlotSpec, ...] = (), page_vm: dict | None = None, meta: dict | None = None) -> PageSpec:
    return PageSpec(id=id, route=route, title=title, slots=slots, page_vm=page_vm or {}, meta=meta or {})

def site(*pages: PageSpec, base_path: str = "/") -> SiteSpec:
    return SiteSpec(base_path=normalize_base_path(base_path), pages=tuple(pages))
