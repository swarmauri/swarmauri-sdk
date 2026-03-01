from __future__ import annotations

try:
    from jinja2 import (
        ChoiceLoader,
        Environment,
        FileSystemLoader,
        PackageLoader,
        TemplateNotFound,
        select_autoescape,
    )
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    ChoiceLoader = None
    Environment = None
    FileSystemLoader = None
    PackageLoader = None

    class TemplateNotFound(Exception):
        """Fallback exception used when jinja2 is unavailable."""

    def select_autoescape(*_: object, **__: object) -> None:
        """Fallback no-op used when jinja2 is unavailable."""

        return None


__all__ = [
    "Environment",
    "FileSystemLoader",
    "PackageLoader",
    "ChoiceLoader",
    "select_autoescape",
    "TemplateNotFound",
]
