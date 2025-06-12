"""Reusable TUI widgets for Peagen."""

from .footer import DashboardFooter
from .tree_view import FileTree
from .log_view import LogView
from .metrics_tab import MetricsTab
from .workers_view import WorkersView
from .templates_view import TemplatesView

__all__ = [
    "DashboardFooter",
    "FileTree",
    "LogView",
    "MetricsTab",
    "WorkersView",
    "TemplatesView",
]

