# tigrbl_client/_nested_crud.py
"""Helpers for constructing canonical Tigrbl REST paths.

The canonical route shapes are:
- ``/{collection}/__/{id}``
- ``/{collection}/__/{id}/{member_op}``
- ``/{collection}/__/{id}/{child_collection}/__/{child_id}``
- ``/{collection}/__/{id}/{child_collection}/__/{child_id}/{member_op}``
- ``/{collection}/{collection_op}``
"""

from __future__ import annotations

from urllib.parse import quote


class NestedCRUDMixin:
    """Utility methods for generating canonical Tigrbl REST paths."""

    @staticmethod
    def _segment(value: str | int) -> str:
        """Encode a path segment safely for URL usage."""
        return quote(str(value), safe="")

    @classmethod
    def collection_path(cls, collection: str, collection_op: str | None = None) -> str:
        """Build ``/{collection}`` or ``/{collection}/{collection_op}``."""
        base = f"/{cls._segment(collection)}"
        if collection_op:
            return f"{base}/{cls._segment(collection_op)}"
        return base

    @classmethod
    def member_path(
        cls,
        collection: str,
        item_id: str | int,
        member_op: str | None = None,
    ) -> str:
        """Build ``/{collection}/__/{id}`` with optional member operation."""
        path = f"/{cls._segment(collection)}/__/{cls._segment(item_id)}"
        if member_op:
            return f"{path}/{cls._segment(member_op)}"
        return path

    @classmethod
    def child_member_path(
        cls,
        collection: str,
        item_id: str | int,
        child_collection: str,
        child_id: str | int,
        member_op: str | None = None,
    ) -> str:
        """Build nested member paths with optional member operation."""
        path = (
            f"/{cls._segment(collection)}/__/{cls._segment(item_id)}"
            f"/{cls._segment(child_collection)}/__/{cls._segment(child_id)}"
        )
        if member_op:
            return f"{path}/{cls._segment(member_op)}"
        return path
