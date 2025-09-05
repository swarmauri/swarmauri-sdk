"""Endpoint factory helpers for REST bindings."""

from .collection import _make_collection_endpoint
from .member import _make_member_endpoint

__all__ = ["_make_collection_endpoint", "_make_member_endpoint"]
