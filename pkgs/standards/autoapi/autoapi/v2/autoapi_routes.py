"""
autoapi_routes.py
Helpers that build path prefixes for nested REST endpoints.
The logic is intentionally minimal; extend or override as needed.
"""
from __future__ import annotations
from typing import Type


def _nested_prefix(self, model: Type) -> str:
    """
    Return a hierarchical prefix for *model*.

    Rules:
    1. If the SQLAlchemy model defines `_nested_path` (str), use it verbatim.
       Example:
           class Workspace(Base):
               __tablename__ = "workspaces"
               _nested_path  = "/tenants/{tenant_id}/workspaces"
    2. Otherwise default to '/{table_name}'.

    You may monkey-patch `AutoAPI._nested_prefix` at runtime or fork this
    helper to implement more sophisticated conventions (e.g. inspecting
    foreign-key chains, pluralisation rules, etc.).
    """
    return getattr(model, "_nested_path", f"/{model.__tablename__}")
