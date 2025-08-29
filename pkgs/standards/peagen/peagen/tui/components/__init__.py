"""Reusable TUI widgets for Peagen."""

from peagen.tui.components.footer import DashboardFooter
from peagen.tui.components.tree_view import FileTree
from peagen.tui.components.log_view import LogView
from peagen.tui.components.metrics_tab import MetricsTab
from peagen.tui.components.workers_view import WorkersView
from peagen.tui.components.templates_view import TemplatesView
from peagen.tui.components.reconnect_screen import ReconnectScreen
from peagen.tui.components.task_detail_screen import TaskDetailScreen
from peagen.tui.components.number_input_screen import NumberInputScreen
from peagen.tui.components.task_table import TaskTable
from peagen.tui.components.filter_bar import FilterBar

__all__ = [
    "DashboardFooter",
    "FileTree",
    "LogView",
    "MetricsTab",
    "WorkersView",
    "TemplatesView",
    "ReconnectScreen",
    "TaskDetailScreen",
    "NumberInputScreen",
    "TaskTable",
    "FilterBar",
]
