"""Utilities for generating project slugs."""

import re
from urllib.parse import urlparse


def slugify(name: str) -> str:
    """Return a filesystem-friendly slug version of *name*."""
    slug = re.sub(r"[^0-9A-Za-z_-]+", "-", name).strip("-")
    return slug.lower()


def repo_slug(repo: str) -> str:
    """Return a tenant slug derived from a GitHub reference or repo URL."""
    if repo.startswith("gh://"):
        repo = repo[5:]
    if repo.startswith("git+"):
        repo = repo[4:].split("@", 1)[0]
    if repo.startswith("http://") or repo.startswith("https://"):
        parsed = urlparse(repo)
        if "github.com" in parsed.netloc:
            repo = parsed.path.lstrip("/")
    repo = repo.rstrip(".git")
    repo = repo.replace("/", "-")
    return slugify(repo)
