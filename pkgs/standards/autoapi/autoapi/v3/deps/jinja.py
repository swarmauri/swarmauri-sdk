from __future__ import annotations

try:  # pragma: no cover - optional dependency
    from jinja2 import (
        Environment,
        FileSystemLoader,
        PackageLoader,
        ChoiceLoader,
        select_autoescape,
        TemplateNotFound,
    )
except Exception:  # pragma: no cover
    Environment = None  # type: ignore
    FileSystemLoader = None  # type: ignore
    PackageLoader = None  # type: ignore
    ChoiceLoader = None  # type: ignore
    select_autoescape = None  # type: ignore
    TemplateNotFound = None  # type: ignore

__all__ = [
    "Environment",
    "FileSystemLoader",
    "PackageLoader",
    "ChoiceLoader",
    "select_autoescape",
    "TemplateNotFound",
]
