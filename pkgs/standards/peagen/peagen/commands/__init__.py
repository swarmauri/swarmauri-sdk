"""Expose all Typer sub-applications for the CLI."""

from peagen.commands.init import init_app
from peagen.commands.process import process_app
from peagen.commands.revise import revise_app
from peagen.commands.sort import sort_app
from peagen.commands.templates import template_sets_app
from peagen.commands.doe import doe_app
from peagen.commands.program import program_app
from peagen.commands.validate import validate_app
from peagen.commands.extras import extras_app

__all__ = [
    "init_app",
    "process_app",
    "revise_app",
    "sort_app",
    "template_sets_app",
    "doe_app",
    "program_app",
    "validate_app",
    "extras_app",
]
