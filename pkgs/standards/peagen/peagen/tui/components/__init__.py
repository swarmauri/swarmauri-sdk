"""Reusable TUI widgets for Peagen."""

from .footer import DashboardFooter
from .tree_view import FileTree
from .log_view import LogView
from .metrics_tab import MetricsTab
from .workers_view import WorkersView
from .templates_view import TemplatesView
from .reconnect_screen import ReconnectScreen
from .task_detail_screen import TaskDetailScreen

__all__ = [
    "DashboardFooter",
    "FileTree",
    "LogView",
    "MetricsTab",
    "WorkersView",
    "TemplatesView",
    "ReconnectScreen",
    "TaskDetailScreen",
]

