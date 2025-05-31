"""Utilities for generating project slugs."""

import re


def slugify(name: str) -> str:
    """Return a filesystem-friendly slug version of *name*."""
    slug = re.sub(r"[^0-9A-Za-z_-]+", "-", name).strip("-")
    return slug.lower()
