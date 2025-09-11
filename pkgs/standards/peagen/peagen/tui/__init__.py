"""Textual user interface helpers for Peagen."""

from typing import TYPE_CHECKING

__all__ = [
    "QueueDashboardApp",
    "TaskStreamClient",
    "download_remote",
    "upload_remote",
]

if TYPE_CHECKING:  # pragma: no cover - used only for type checkers
    from peagen.tui.app import QueueDashboardApp
    from peagen.tui.ws_client import TaskStreamClient
    from peagen.tui.fileops import download_remote, upload_remote


def __getattr__(name: str):
    if name == "QueueDashboardApp":
        from peagen.tui.app import QueueDashboardApp as _QueueDashboardApp

        return _QueueDashboardApp
    if name == "TaskStreamClient":
        from peagen.tui.ws_client import TaskStreamClient as _TaskStreamClient

        return _TaskStreamClient
    if name == "download_remote":
        from peagen.tui.fileops import download_remote as _download_remote

        return _download_remote
    if name == "upload_remote":
        from peagen.tui.fileops import upload_remote as _upload_remote

        return _upload_remote
    raise AttributeError(name)
