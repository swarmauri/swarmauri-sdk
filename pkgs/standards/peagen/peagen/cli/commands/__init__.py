"""Expose all Typer sub-applications for the CLI."""

from .doe import doe_app
from .eval import eval_app
from .extras import extras_app
from .fetch import fetch_app
from .init import init_app
from .process import process_app
from .sort import sort_app
from .templates import template_sets_app
from .validate import validate_app

__all__ = [
    "doe_app",
    "eval_app",
    "extras_app",
    "fetch_app",
    "init_app",
    "process_app",
    "sort_app",
    "template_sets_app",
    "validate_app",
]
