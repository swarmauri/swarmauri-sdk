"""Compatibility wrappers for FastAPI dependency helpers."""

from fastapi import Depends, Security
from fastapi.params import Depends as Dependency

__all__ = ["Depends", "Security", "Dependency"]
