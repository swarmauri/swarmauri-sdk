from __future__ import annotations

import asyncio
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List
import math
from urllib.parse import urlparse

import httpx
from textual import events
from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.coordinate import Coordinate
from textual.reactive import reactive
from textual.widget import NoMatches
from textual.widgets import (
    DataTable,
    Header,
    Input,
    Label,  # Added Label
    Select,
    TabbedContent,
    TabPane,
    TextArea,
    Tree,
)

from peagen.tui.components import (
    DashboardFooter,
    FileTree,
    FilterBar,
    ReconnectScreen,
    TaskDetailScreen,
    NumberInputScreen,
    TaskTable,
    TemplatesView,
    WorkersView,
)
from peagen.tui.fileops import download_remote, upload_remote
from peagen.tui.ws_client import TaskStreamClient


def clipboard_copy(text: str) -> None:
    platform = sys.platform
    if platform.startswith("win"):
        with subprocess.Popen(["clip"], stdin=subprocess.PIPE, text=True) as proc:
            proc.communicate(text)
    elif platform.startswith("darwin"):
        with subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE, text=True) as proc:
            proc.communicate(text)
    else:
        with subprocess.Popen(
            ["xclip", "-selection", "clipboard"], stdin=subprocess.PIPE, text=True
        ) as proc:
            proc.communicate(text)


def clipboard_paste() -> str:
    platform = sys.platform
    if platform.startswith("win"):
        completed = subprocess.run(
            ["powershell", "-command", "Get-Clipboard"],
            capture_output=True,
            text=True,
        )
        return completed.stdout
    if platform.startswith("darwin"):
        completed = subprocess.run(["pbpaste"], capture_output=True, text=True)
        return completed.stdout
    completed = subprocess.run(
        ["xclip", "-selection", "clipboard", "-o"],
        capture_output=True,
        text=True,
    )
    return completed.stdout


def _format_ts(ts: float | str | None) -> str:
    if ts is None:
        return ""
    try:
        if isinstance(ts, str):
            dt_obj = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            return dt_obj.isoformat(timespec="seconds")
        return datetime.utcfromtimestamp(float(ts)).isoformat(timespec="seconds")
    except Exception:
        return str(ts)


def _calc_duration(start: float | str | None, finish: float | str | None) -> int | None:
    """Return elapsed seconds between ``start`` and ``finish`` if possible."""

    if start is None or finish is None:
        return None
    try:
        if isinstance(start, str):
            start_ts = datetime.fromisoformat(start.replace("Z", "+00:00")).timestamp()
        else:
            start_ts = float(start)
        if isinstance(finish, str):
            finish_ts = datetime.fromisoformat(
                finish.replace("Z", "+00:00")
            ).timestamp()
        else:
            finish_ts = float(finish)
        return int(finish_ts - start_ts)
    except Exception:
        return None


def _truncate_id(task_id: str, length: int = 4) -> str:
    """Return a shortened representation of *task_id*.

    If the ID is longer than ``2 * length`` characters, the output keeps the
    first and last ``length`` characters separated by an ellipsis.

    Args:
        task_id: The full task identifier string.
        length: Number of characters to show at both ends.

    Returns:
        The truncated ID for display.
    """

    if len(task_id) <= length * 2:
        return task_id
    return f"{task_id[:length]}...{task_id[-length:]}"


class RemoteBackend:
    def __init__(self, gateway_url: str) -> None:
        self.rpc_url = gateway_url.rstrip("/") + "/rpc"
        self.http = httpx.AsyncClient(timeout=10.0)
        self.tasks: List[dict] = []
        self.workers: Dict[str, dict] = {}
        self.last_error: str | None = None

    async def refresh(self, limit: int | None = None, offset: int = 0) -> bool:
        try:
            await asyncio.gather(
                self.fetch_tasks(limit=limit, offset=offset), self.fetch_workers()
            )
        except Exception as exc:
            self.last_error = str(exc)
            return False
        else:
            self.last_error = None
            return True

    async def fetch_tasks(self, limit: int | None = None, offset: int = 0) -> None:
        params: dict[str, int | str] = {"poolName": "default"}
        if limit is not None:
            params["limit"] = int(limit)
        if offset:
            params["offset"] = int(offset)
        payload = {
            "jsonrpc": "2.0",
            "id": "1",
            "method": "Pool.listTasks",
            "params": params,
        }
        resp = await self.http.post(self.rpc_url, json=payload)
        resp.raise_for_status()
        self.tasks = resp.json().get("result", [])

    async def fetch_workers(self) -> None:
        payload = {
            "jsonrpc": "2.0",
            "id": "2",
            "method": "Worker.list",
            "params": {},
        }
        resp = await self.http.post(self.rpc_url, json=payload)
        resp.raise_for_status()
        raw_workers = resp.json().get("result", [])
        workers: Dict[str, dict] = {}
        for entry in raw_workers:
            info = {**entry}
            ts_raw = info.get("last_seen")
            try:
                ts = datetime.utcfromtimestamp(int(ts_raw)) if ts_raw else None
            except (TypeError, ValueError):
                ts = None
            info["last_seen"] = ts
            for k, v in list(info.items()):
                if isinstance(v, str) and (v.startswith("{") or v.startswith("[")):
                    try:
                        info[k] = json.loads(v)
                    except Exception:
                        pass
            workers[info["id"]] = info
        self.workers = workers


class QueueDashboardApp(App):
    CSS = """
    TabPane#editor { height: 1fr; width:  1fr; }
    TextArea#code_editor { height: 1fr; width:  1fr; }

    /* Styles for the filter section to ensure visibility */
    #filter-section-container {
        padding: 0 1; /* Horizontal padding */
        margin-bottom: 1; /* Gap below the entire filter section */
        /* Fixed height: Label (1) + Label's padding-bottom (1) + FilterBar (1, assuming compact Selects) */
        height: 3; 
    }

    #filter-title-label {
        padding-bottom: 1; /* Space between "Filter" title and the FilterBar */
        text-style: bold;
        /* The Label widget itself is typically 1 cell high */
    }

    /* Ensure the main TabbedContent (holding Pools, Tasks, etc.) takes up the remaining space */
    /* This targets the TabbedContent that is a direct child of the main Vertical layout container */
    Vertical > TabbedContent {
        height: 1fr; /* Takes up the remaining flexible vertical space */
    }
    """
    TITLE = "Peagen"
    BINDINGS = [
        ("1", "switch('pools')", "Pools"),
        ("2", "switch('tasks')", "Tasks"),
        ("3", "switch('errors')", "Errors"),
        ("4", "switch('artifacts')", "Artifacts"),
        ("5", "switch('templates')", "Templates"),
        ("ctrl+s", "save_file", "Save"),
        ("c", "toggle_children", "Collapse"),
        ("space", "toggle_children", "Collapse"),
        ("ctrl+c", "copy_selection", "Copy"),
        ("ctrl+p", "paste_clipboard", "Paste"),
        ("s", "cycle_sort", "Sort"),
        ("escape", "clear_filters", "Clear Filters"),
        ("n", "next_page", "Next Page"),
        ("p", "prev_page", "Prev Page"),
        ("l", "set_limit", "Limit"),
        ("j", "jump_page", "Jump Page"),
        ("q", "quit", "Quit"),
    ]

    SORT_KEYS = [
        "time",
        "pool",
        "status",
        "action",
        "label",
        "duration",
        "id",
        "date_created",
        "last_modified",
        "error",
    ]

    LIMIT_OPTIONS = [10, 20, 50, 100]

    COLUMN_LABEL_TO_SORT_KEY = {
        "ID": "id",
        "Pool": "pool",
        "Status": "status",
        "Action": "action",
        "Labels": "label",
        "Started": "date_created",
        "Finished": "last_modified",
        "Duration (s)": "duration",
        "Error": "error",
    }

    queue_len = reactive(0)
    done_len = reactive(0)
    fail_len = reactive(0)
    worker_len = reactive(0)

    def __init__(self, gateway_url: str = "http://localhost:8000") -> None:
        super().__init__()
        ws_url = gateway_url.replace("http", "ws").rstrip("/") + "/ws/tasks"
        self.client = TaskStreamClient(ws_url)
        self.backend = RemoteBackend(gateway_url)
        self.sort_key = "time"
        self.sort_reverse = False
        self.filter_id: str | None = None
        self.filter_pool: str | None = None
        self.filter_status: str | None = None
        self.filter_action: str | None = None
        self.filter_label: str | None = None
        self.collapsed: set[str] = set()
        self._seen_parents: set[str] = set()
        self._reconnect_screen: ReconnectScreen | None = None
        self._filter_debounce_timer = None
        self._current_file: str | None = None
        self._remote_info: tuple | None = None
        self.ws_connected = False  # Track WebSocket connection status
        self.limit = 50
        self.offset = 0

    async def on_mount(self):
        # Register for connection status changes
        self.client.on_connection_change(self.on_websocket_connection_change)

        self.run_worker(
            self.client.listen(), exclusive=True, group="websocket_listener"
        )
        self.set_interval(1.0, self._refresh_backend_and_ui)
        self.trigger_data_processing()

    async def on_websocket_connection_change(
        self, is_connected: bool, error_msg: str
    ) -> None:
        """Handle websocket connection status changes."""
        self.ws_connected = is_connected

        if not is_connected:
            # Show reconnect screen for websocket disconnection
            await self._show_reconnect(f"WebSocket disconnected: {error_msg}")
        elif is_connected and self._reconnect_screen:
            # Only dismiss if the backend is also connected
            ok = await self.backend.refresh(limit=self.limit, offset=self.offset)
            if ok:
                await self._dismiss_reconnect()
                self.toast("Connection re-established", duration=2.0)
                self.trigger_data_processing(debounce=False)

    async def _refresh_backend_and_ui(self) -> None:
        if self._reconnect_screen:
            return

        ok = await self.backend.refresh(limit=self.limit, offset=self.offset)

        # Handle backend API connection issues
        if not ok and not self._reconnect_screen:
            await self._show_reconnect(self.backend.last_error or "Connection failed")
        # Only dismiss reconnect screen if both backend and websocket are working
        elif ok and self.ws_connected and self._reconnect_screen:
            await self._dismiss_reconnect()

        # Always update the UI if possible
        self.trigger_data_processing(debounce=False)

    async def retry_connection(self) -> None:
        # Restart the websocket listener
        self.run_worker(
            self.client.listen(), exclusive=True, group="websocket_listener_retry"
        )

        # Try to refresh backend data
        ok = await self.backend.refresh(limit=self.limit, offset=self.offset)

        # Only dismiss if both backend and websocket are connected
        if ok and self.ws_connected:
            await self._dismiss_reconnect()
        else:
            # Update the message with the current error state
            error_msg = self.backend.last_error or "Connection failed"
            if not self.ws_connected:
                error_msg = f"WebSocket disconnected. {error_msg}"

            if self._reconnect_screen:
                self._reconnect_screen.message = error_msg
            else:
                await self._show_reconnect(error_msg)

    def trigger_data_processing(self, debounce: bool = True) -> None:
        if debounce:
            if self._filter_debounce_timer is not None:
                self._filter_debounce_timer.stop()
            self._filter_debounce_timer = self.set_timer(
                0.3,
                lambda: self.run_worker(
                    self.async_process_and_update_data(),
                    exclusive=True,
                    group="data_refresh_worker",
                ),
                name="filter_debounce_timer",
            )
        else:
            self.run_worker(
                self.async_process_and_update_data(),
                exclusive=True,
                group="data_refresh_worker",
            )

    async def on_select_changed(self, event: Select.Changed) -> None:
        event.stop()
        value = str(event.value) if event.value != Select.BLANK else None
        filter_changed = False

        if event.control.id == "filter_id":
            if self.filter_id != value:
                self.filter_id = value
                filter_changed = True
        elif event.control.id == "filter_pool":
            if self.filter_pool != value:
                self.filter_pool = value
                filter_changed = True
        elif event.control.id == "filter_status":
            if self.filter_status != value:
                self.filter_status = value
                filter_changed = True
        elif event.control.id == "filter_action":
            if self.filter_action != value:
                self.filter_action = value
                filter_changed = True
        elif event.control.id == "filter_label":
            if self.filter_label != value:
                self.filter_label = value
                filter_changed = True

        if filter_changed:
            self.trigger_data_processing()

    async def on_input_changed(self, event: Input.Changed) -> None:
        event.stop()
        value = event.value.strip() if event.value else None
        filter_changed = False

        if event.input.id == "filter_id":
            if self.filter_id != value:
                self.filter_id = value
                filter_changed = True

        if filter_changed:
            self.trigger_data_processing()

    async def async_process_and_update_data(self) -> None:
        all_tasks_from_client = list(self.client.tasks.values())
        all_tasks_from_backend = list(self.backend.tasks)

        combined_tasks_dict: Dict[str, Any] = {}
        for task in all_tasks_from_backend + all_tasks_from_client:
            tid = task.get("id")
            if tid is not None:
                combined_tasks_dict[tid] = task
        all_tasks = list(combined_tasks_dict.values())

        for task in all_tasks:
            result_data = task.get("result") or {}
            if result_data.get("children"):
                tid_str = str(task.get("id"))
                if tid_str not in self._seen_parents:
                    self._seen_parents.add(tid_str)
                    self.collapsed.add(tid_str)

        current_filter_criteria = {
            "id": self.filter_id,
            "pool": self.filter_pool,
            "status": self.filter_status,
            "action": self.filter_action,
            "label": self.filter_label,
            "sort_key": self.sort_key,
            "sort_reverse": self.sort_reverse,
            "collapsed": self.collapsed.copy(),
        }
        processed_data = self._perform_filtering_and_sorting(
            all_tasks,
            current_filter_criteria,
            limit=self.limit,
            offset=self.offset,
        )
        self.call_later(self._update_ui_with_processed_data, processed_data, all_tasks)

    def _perform_filtering_and_sorting(
        self,
        tasks_input: list,
        criteria: dict,
        *,
        limit: int | None = None,
        offset: int = 0,
    ) -> dict:
        tasks = list(tasks_input)

        if criteria.get("id"):
            tasks = [t for t in tasks if str(t.get("id")) == criteria["id"]]
        if criteria.get("pool"):
            tasks = [t for t in tasks if t.get("pool") == criteria["pool"]]
        if criteria.get("status"):
            tasks = [t for t in tasks if t.get("status") == criteria["status"]]
        if criteria.get("action"):
            tasks = [t for t in tasks if t.get("action") == criteria["action"]]
        if criteria.get("label"):
            tasks = [t for t in tasks if criteria["label"] in t.get("labels", [])]

        for t in tasks:
            if t.get("duration") is None:
                t["duration"] = _calc_duration(
                    t.get("date_created"), t.get("last_modified")
                )

        sort_key = criteria.get("sort_key")
        sort_reverse = criteria.get("sort_reverse", False)
        if sort_key:

            def _key_func(task_item):
                if sort_key == "action":
                    return task_item.get("action")
                if sort_key == "label":
                    return ",".join(task_item.get("labels", []))
                if sort_key == "duration":
                    return task_item.get("duration") or 0
                if sort_key == "time":
                    return (
                        task_item.get("date_created")
                        or task_item.get("last_modified")
                        or 0
                    )
                if sort_key == "status":
                    from peagen.transport.jsonrpc_schemas import Status

                    status_value = task_item.get("status")
                    try:
                        status_index = (
                            list(Status).index(Status(status_value))
                            if status_value
                            else float("inf")
                        )
                        return status_index
                    except (ValueError, TypeError):
                        return float("inf")
                return task_item.get(sort_key)

            tasks_with_val = [t for t in tasks if _key_func(t) is not None]
            tasks_without_val = [t for t in tasks if _key_func(t) is None]
            tasks_with_val.sort(key=_key_func, reverse=sort_reverse)
            tasks = tasks_with_val + tasks_without_val

        current_workers = {}
        source_workers = (
            self.client.workers if self.client.workers else self.backend.workers
        )
        for wid, data in source_workers.items():
            info = {**data}
            ts_raw = info.get("last_seen", datetime.utcnow().timestamp())
            try:
                ts_float = float(ts_raw)
            except (TypeError, ValueError):
                ts_float = datetime.utcnow().timestamp()
            info["last_seen"] = datetime.utcfromtimestamp(ts_float)
            current_workers[wid] = info

        if criteria.get("pool"):
            current_workers = {
                wid: w
                for wid, w in current_workers.items()
                if w.get("pool") == criteria["pool"]
            }

        calculated_metrics = {}
        if self.client.queues:
            calculated_metrics["queue_len"] = sum(self.client.queues.values())
        else:
            calculated_metrics["queue_len"] = sum(
                1 for t in tasks if t.get("status") == "running"
            )
        calculated_metrics["done_len"] = sum(
            1 for t in tasks if t.get("status") == "done"
        )
        calculated_metrics["fail_len"] = sum(
            1 for t in tasks if t.get("status") == "failed"
        )
        calculated_metrics["worker_len"] = len(current_workers)

        page_tasks = tasks
        if limit is not None:
            start = max(0, offset)
            end = start + limit
            page_tasks = tasks[start:end]

        return {
            "tasks_to_display": page_tasks,
            "workers_data": current_workers,
            "metrics_data": calculated_metrics,
            "collapsed_state": criteria["collapsed"],
        }

    def _update_ui_with_processed_data(
        self, processed_data: dict, all_tasks_for_options: list
    ) -> None:
        tasks_to_display = processed_data["tasks_to_display"]
        workers_data = processed_data["workers_data"]
        metrics_data = processed_data["metrics_data"]

        self.queue_len = metrics_data.get("queue_len", 0)
        self.done_len = metrics_data.get("done_len", 0)
        self.fail_len = metrics_data.get("fail_len", 0)
        self.worker_len = metrics_data.get("worker_len", 0)

        current_page = self.offset // self.limit + 1
        total_pages = max(1, math.ceil(self.queue_len / self.limit))

        if hasattr(self, "workers_view"):
            self.workers_view.update_workers(workers_data)

        if hasattr(self, "filter_bar"):
            self.filter_bar.update_options(all_tasks_for_options)

        if hasattr(self, "tasks_table"):
            current_cursor_row = self.tasks_table.cursor_row
            current_cursor_column = self.tasks_table.cursor_column
            current_scroll_x = self.tasks_table.scroll_x
            current_scroll_y = self.tasks_table.scroll_y
            self.tasks_table.clear()
            seen_task_ids: set[str] = set()

            for t_data in tasks_to_display:
                task_id = str(t_data.get("id", ""))
                if not task_id or task_id in seen_task_ids:
                    continue
                prefix = ""
                result_data = t_data.get("result") or {}
                children_ids = result_data.get("children", [])
                if children_ids:
                    # Display '-' when expanded and '+' when collapsed
                    prefix = "- " if task_id not in self.collapsed else "+ "

                self.tasks_table.add_row(
                    f"{prefix}{_truncate_id(task_id)}",
                    t_data.get("pool", ""),
                    t_data.get("status", ""),
                    t_data.get("action", ""),
                    ",".join(t_data.get("labels", [])),
                    _format_ts(t_data.get("date_created")),
                    _format_ts(t_data.get("last_modified")),
                    str(t_data.get("duration", ""))
                    if t_data.get("duration") is not None
                    else "",
                    key=task_id,
                )
                seen_task_ids.add(task_id)

                if children_ids and task_id not in self.collapsed:
                    for child_id_str in children_ids:
                        child_task = next(
                            (
                                ct
                                for ct in tasks_to_display
                                if str(ct.get("id")) == str(child_id_str)
                            ),
                            None,
                        )
                        if child_task and str(child_id_str) not in seen_task_ids:
                            self.tasks_table.add_row(
                                f"  {_truncate_id(str(child_id_str))}",
                                child_task.get("pool", ""),
                                child_task.get("status", ""),
                                child_task.get("action", ""),
                                ",".join(child_task.get("labels", [])),
                                _format_ts(child_task.get("date_created")),
                                _format_ts(child_task.get("last_modified")),
                                str(child_task.get("duration", ""))
                                if child_task.get("duration") is not None
                                else "",
                                key=str(child_id_str),
                            )
                            seen_task_ids.add(str(child_id_str))

            if (
                current_cursor_row is not None
                and current_cursor_row < self.tasks_table.row_count
            ):
                self.tasks_table.cursor_coordinate = Coordinate(
                    current_cursor_row, current_cursor_column or 0
                )
            elif self.tasks_table.row_count > 0:
                self.tasks_table.cursor_coordinate = Coordinate(0, 0)

            self.tasks_table.scroll_x = min(
                current_scroll_x, self.tasks_table.max_scroll_x
            )
            self.tasks_table.scroll_y = min(
                current_scroll_y, self.tasks_table.max_scroll_y
            )

        if hasattr(self, "err_table"):
            current_err_cursor_row = self.err_table.cursor_row
            current_err_cursor_column = self.err_table.cursor_column
            err_scroll_x = self.err_table.scroll_x
            err_scroll_y = self.err_table.scroll_y
            self.err_table.clear()
            if metrics_data.get("fail_len", 0) > 0:
                for t_data in (
                    t for t in tasks_to_display if t.get("status") == "failed"
                ):
                    err_file = t_data.get("error_file", "")
                    link = f"[link=file://{err_file}]open[/link]" if err_file else ""
                    task_id = str(t_data.get("id", ""))
                    result_data = t_data.get("result", {}) or {}
                    err_msg = result_data.get("error", "")
                    self.err_table.add_row(
                        _truncate_id(task_id),
                        t_data.get("pool", ""),
                        t_data.get("status", ""),
                        t_data.get("action", ""),
                        ",".join(t_data.get("labels", [])),
                        _format_ts(t_data.get("date_created")),
                        _format_ts(t_data.get("last_modified")),
                        str(t_data.get("duration", ""))
                        if t_data.get("duration") is not None
                        else "",
                        f"{err_msg} {link}".strip(),
                        key=task_id,
                    )
            if (
                current_err_cursor_row is not None
                and current_err_cursor_row < self.err_table.row_count
            ):
                self.err_table.cursor_coordinate = Coordinate(
                    current_err_cursor_row, current_err_cursor_column or 0
                )
            elif self.err_table.row_count > 0:
                self.err_table.cursor_coordinate = Coordinate(0, 0)

            self.err_table.scroll_x = min(err_scroll_x, self.err_table.max_scroll_x)
            self.err_table.scroll_y = min(err_scroll_y, self.err_table.max_scroll_y)

        current_page = self.offset // self.limit + 1
        total_pages = max(1, math.ceil(self.queue_len / self.limit))
        if hasattr(self, "footer"):
            current_page = self.offset // self.limit + 1
            total_pages = max(1, math.ceil(self.queue_len / self.limit))
            self.footer.set_page_info(current_page, total_pages)
        self.sub_title = f"Page {current_page} of {total_pages}"

    async def on_open_url(self, event: events.OpenURL) -> None:
        if event.url.startswith("file://"):
            event.prevent_default()
            event.stop()
            await self.open_editor(event.url.removeprefix("file://"))
        if event.url.startswith("oid:"):
            event.prevent_default()
            event.stop()
            await self.open_git_oid(event.url.removeprefix("oid:"))

    async def on_file_tree_file_selected(self, message: FileTree.FileSelected) -> None:
        message.stop()
        await self.open_editor(message.path.as_posix())

    def toast(
        self, message: str, *, style: str = "information", duration: float | None = 2.0
    ) -> None:
        if hasattr(self, "notify"):
            self.notify(message, severity=style, timeout=duration)
        else:
            self.log(f"[{style.upper()}] {message}")

    def compose(self) -> ComposeResult:
        yield Header()
        self.workers_view = WorkersView(id="workers_view")
        self.file_tree = FileTree("tree", id="file_tree")
        self.templates_tree = TemplatesView(id="templates_tree")
        self.tasks_table = TaskTable(self.open_task_detail, id="tasks_table")
        self.tasks_table.add_columns(
            "ID",
            "Pool",
            "Status",
            "Action",
            "Labels",
            "Started",
            "Finished",
            "Duration (s)",
        )
        self.tasks_table.cursor_type = "cell"

        self.err_table = TaskTable(self.open_task_detail, id="err_table")
        self.err_table.add_columns(
            "ID",
            "Pool",
            "Status",
            "Action",
            "Labels",
            "Started",
            "Finished",
            "Duration (s)",
            "Error",
        )
        self.err_table.cursor_type = "cell"

        self.file_tabs = TabbedContent(id="file_tabs")
        self.file_tabs.display = False
        self.filter_bar = FilterBar()

        with Vertical():
            with Vertical(id="filter-section-container"):
                yield Label("Filter", id="filter-title-label")
                yield self.filter_bar
            with TabbedContent(initial="pools"):
                yield TabPane("Pools", self.workers_view, id="pools")
                yield TabPane("Tasks", self.tasks_table, id="tasks")
                yield TabPane("Errors", self.err_table, id="errors")
                yield TabPane("Artifacts", self.file_tree, id="artifacts")
                yield TabPane("Templates", self.templates_tree, id="templates")

        yield self.file_tabs
        self.footer = DashboardFooter()
        yield self.footer
        self.call_later(self.tasks_table.focus)

    def action_switch(self, tab_id: str) -> None:
        try:
            main_tab_content = self.query(TabbedContent).first()
            main_tab_content.active = tab_id
        except NoMatches:
            self.toast(
                f"Could not switch to tab ID '{tab_id}'. Main TabbedContent not found.",
                style="error",
            )

    def action_save_file(self) -> None:
        if not self._current_file:
            self.toast("No file loaded.", style="yellow")
            return

        active_pane = self.file_tabs.active_pane
        if not active_pane:
            self.toast("No active file tab to save.", style="yellow")
            return

        try:
            editor = active_pane.query_one(TextArea)
        except NoMatches:
            self.toast("Could not find editor in the active tab.", style="error")
            return

        text_to_save = editor.text
        if self._remote_info:
            adapter, key, tmp_path_obj = self._remote_info
            Path(tmp_path_obj).write_text(text_to_save, encoding="utf-8")
            try:
                upload_remote(adapter, key, Path(tmp_path_obj))
                self.toast("Uploaded remote file", style="success")
            except Exception as exc:
                self.toast(f"Upload failed: {exc}", style="error")
        else:
            try:
                Path(self._current_file).write_text(text_to_save, encoding="utf-8")
                self.toast(f"Saved {self._current_file}", style="success")
            except Exception as exc:
                self.toast(f"Save failed: {exc}", style="error")

    def action_toggle_children(self) -> None:
        row = self.tasks_table.cursor_row
        if row is None:
            return
        if hasattr(self.tasks_table, "get_row_key"):
            row_key = self.tasks_table.get_row_key(row)
        else:
            row_obj = (
                self.tasks_table.get_row_at(row)
                if hasattr(self.tasks_table, "get_row_at")
                else None
            )
            row_key = getattr(row_obj, "key", None) if row_obj else None
        if row_key is None:
            return
        row_key_str = str(row_key)
        if row_key_str in self.collapsed:
            self.collapsed.remove(row_key_str)
        else:
            self.collapsed.add(row_key_str)
        self.trigger_data_processing()

    def action_cycle_sort(self) -> None:
        try:
            idx = self.SORT_KEYS.index(self.sort_key)
        except ValueError:
            idx = 0
        self.sort_key = self.SORT_KEYS[(idx + 1) % len(self.SORT_KEYS)]
        self.sort_reverse = False
        self.toast(f"Sorting by {self.sort_key}", duration=1.0)
        self.trigger_data_processing()

    def action_filter_by_cell(self) -> None:
        row = self.tasks_table.cursor_row
        col = self.tasks_table.cursor_column
        if row is None or col is None:
            return
        value = (
            self.tasks_table.get_cell_at(Coordinate(row, col))
            if hasattr(self.tasks_table, "get_cell_at")
            else self.tasks_table.get_cell(row, col)
        )

        col_label_widget = self.tasks_table.columns[col].label
        col_label = str(col_label_widget)

        filter_changed = False
        str_value = str(value)

        if col_label == "Pool":
            if self.filter_pool != str_value:
                self.filter_pool = None if self.filter_pool == str_value else str_value
                filter_changed = True
        elif col_label == "Status":
            if self.filter_status != str_value:
                self.filter_status = (
                    None if self.filter_status == str_value else str_value
                )
                filter_changed = True
        elif col_label == "Action":
            if self.filter_action != str_value:
                self.filter_action = (
                    None if self.filter_action == str_value else str_value
                )
                filter_changed = True
        elif col_label == "Labels":
            lbl = str_value.split(",")[0] if str_value else ""
            if self.filter_label != lbl:
                self.filter_label = None if self.filter_label == lbl else lbl
                filter_changed = True

        if filter_changed:
            if hasattr(self, "filter_bar"):
                if col_label == "Pool":
                    self.filter_bar.pool_select.value = (
                        self.filter_pool
                        if self.filter_pool is not None
                        else Select.BLANK
                    )
                elif col_label == "Status":
                    self.filter_bar.status_select.value = (
                        self.filter_status
                        if self.filter_status is not None
                        else Select.BLANK
                    )
                elif col_label == "Action":
                    self.filter_bar.action_select.value = (
                        self.filter_action
                        if self.filter_action is not None
                        else Select.BLANK
                    )
                elif col_label == "Labels":
                    self.filter_bar.label_select.value = (
                        self.filter_label
                        if self.filter_label is not None
                        else Select.BLANK
                    )
            self.trigger_data_processing()

    def action_clear_filters(self) -> None:
        self.filter_id = None
        self.filter_pool = None
        self.filter_status = None
        self.filter_action = None
        self.filter_label = None
        if hasattr(self, "filter_bar"):
            self.filter_bar.clear()
        self.trigger_data_processing()

    def action_copy_selection(self) -> None:
        """Copy highlighted or focused text to the clipboard."""

        widget = self.focused
        text = ""
        if isinstance(widget, DataTable):
            row = widget.cursor_row
            key_value = None
            if row is not None:
                if hasattr(widget, "ordered_rows"):
                    try:
                        key_value = widget.ordered_rows[row].key
                    except Exception:
                        key_value = None
                if key_value is None and hasattr(widget, "get_row_key"):
                    try:
                        key_value = widget.get_row_key(row)  # type: ignore[attr-defined]
                    except Exception:
                        key_value = None
            if key_value is not None:
                text = str(getattr(key_value, "value", key_value))
            else:
                row, col = widget.cursor_row, widget.cursor_column
                if row is not None and col is not None:
                    value = (
                        widget.get_cell_at(Coordinate(row, col))
                        if hasattr(widget, "get_cell_at")
                        else widget.get_cell(row, col)
                    )
                    text = str(value)
        elif isinstance(widget, TextArea):
            text = widget.selected_text or widget.text
        elif isinstance(widget, Tree):
            node = getattr(widget, "cursor_node", None)
            if node is not None:
                text = str(getattr(node, "label", ""))
        elif hasattr(widget, "selected_text"):
            text = widget.selected_text
        elif hasattr(widget, "text"):
            text = widget.text
        elif hasattr(widget, "value"):
            text = str(widget.value)
        if text:
            clipboard_copy(text)

    def action_paste_clipboard(self) -> None:
        widget = self.focused
        text_to_paste = clipboard_paste()
        if isinstance(widget, TextArea):
            widget.insert_text_at_cursor(text_to_paste)
        elif hasattr(widget, "insert_text_at_cursor"):
            widget.insert_text_at_cursor(text_to_paste)
        elif hasattr(widget, "insert"):
            widget.insert(text_to_paste)

    def action_next_page(self) -> None:
        self.offset += self.limit
        coro = self.backend.refresh(limit=self.limit, offset=self.offset)
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            asyncio.run(coro)
        else:
            self.run_worker(coro, exclusive=True, group="data_refresh_worker")
        self.trigger_data_processing(debounce=False)

    def action_prev_page(self) -> None:
        if self.offset >= self.limit:
            self.offset -= self.limit
            coro = self.backend.refresh(limit=self.limit, offset=self.offset)
            try:
                asyncio.get_running_loop()
            except RuntimeError:
                asyncio.run(coro)
            else:
                self.run_worker(coro, exclusive=True, group="data_refresh_worker")
            self.trigger_data_processing(debounce=False)

    def action_set_limit(self, limit: int | None = None) -> None:
        """Set the number of tasks shown per page."""

        if limit is None:
            try:
                asyncio.get_running_loop()
            except RuntimeError:
                asyncio.run(self._prompt_and_set_limit())
            else:
                self.run_worker(self._prompt_and_set_limit(), exclusive=True)
            return

        if limit <= 0:
            limit = 1
        self.limit = limit
        self.offset = 0
        coro = self.backend.refresh(limit=self.limit, offset=self.offset)
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            asyncio.run(coro)
        else:
            self.run_worker(coro, exclusive=True, group="data_refresh_worker")
        self.trigger_data_processing(debounce=False)

    def action_jump_page(self, page: int | None = None) -> None:
        """Jump directly to *page* if provided or prompt the user."""
        if page is None:
            try:
                asyncio.get_running_loop()
            except RuntimeError:
                asyncio.run(self._prompt_and_jump())
            else:
                self.run_worker(self._prompt_and_jump(), exclusive=True)
            return
        self._apply_jump_page(page)

    def _apply_jump_page(self, page: int) -> None:
        if page <= 0:
            page = 1
        max_page = max(1, math.ceil(self.queue_len / self.limit))
        if page > max_page:
            page = max_page
        self.offset = (page - 1) * self.limit
        coro = self.backend.refresh(limit=self.limit, offset=self.offset)
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            asyncio.run(coro)
        else:
            self.run_worker(coro, exclusive=True, group="data_refresh_worker")
        self.trigger_data_processing(debounce=False)

    async def _prompt_and_jump(self) -> None:
        current_page = self.offset // self.limit + 1
        total_pages = max(1, math.ceil(self.queue_len / self.limit))
        prompt = f"Jump to page (1-{total_pages})"
        page = await self.push_screen_wait(NumberInputScreen(prompt, current_page))
        if page is not None:
            self._apply_jump_page(page)

    async def _prompt_and_set_limit(self) -> None:
        prompt = "Items per page"
        limit = await self.push_screen_wait(NumberInputScreen(prompt, self.limit))
        if limit is not None:
            self.action_set_limit(limit)

    async def on_data_table_cell_selected(self, event: DataTable.CellSelected) -> None:
        if isinstance(event.value, str) and event.value.startswith("[link="):
            path_str = event.value.split("=", 1)[1].split("]", 1)[0]
            await self.open_editor(Path(path_str).as_posix())
            return

        # Selection events no longer open task details automatically.
        return

    async def on_data_table_header_selected(
        self, event: DataTable.HeaderSelected
    ) -> None:
        """Sort a table when the user clicks a column header."""
        table = event.control
        column_key = event.column_key

        reverse = False
        last_key = getattr(table, "_last_sort_key", None)
        last_reverse = getattr(table, "_last_sort_reverse", False)
        if last_key == column_key:
            reverse = not last_reverse

        table.sort(column_key, reverse=reverse)
        table._last_sort_key = column_key
        table._last_sort_reverse = reverse

        label_plain = event.label.plain
        sort_key = self.COLUMN_LABEL_TO_SORT_KEY.get(label_plain)
        if sort_key:
            self.sort_key = sort_key
        self.sort_reverse = reverse
        self.trigger_data_processing(debounce=False)
        event.stop()

    async def open_task_detail(self, task_id: str) -> None:
        task = self.client.tasks.get(task_id)
        if not task:
            task = next(
                (t for t in self.backend.tasks if str(t.get("id")) == task_id), None
            )
        if task:
            await self.push_screen(TaskDetailScreen(task_data=task))
        else:
            self.toast(f"Task details not found for ID: {task_id}", style="warning")

    async def open_editor(self, file_path: str) -> None:
        parsed = urlparse(file_path)
        text = ""
        self._remote_info = None
        self._current_file = None
        actual_file_path = file_path

        if parsed.scheme and parsed.scheme != "file":
            try:
                tmp_path_obj, adapter, key = download_remote(file_path)
                self._remote_info = (adapter, key, tmp_path_obj)
                text = tmp_path_obj.read_text(encoding="utf-8")
                self._current_file = tmp_path_obj.as_posix()
                actual_file_path = file_path
            except Exception as exc:
                self.toast(f"Cannot download {file_path}: {exc}", style="error")
                return
        else:
            local_path = Path(file_path)
            try:
                text = local_path.read_text(encoding="utf-8")
                self._current_file = local_path.as_posix()
                actual_file_path = self._current_file
            except Exception as exc:
                self.toast(f"Cannot open {file_path}: {exc}", style="error")
                return

        pane_id = actual_file_path
        lang_map = {
            ".py": "python",
            ".js": "javascript",
            ".json": "json",
            ".yaml": "yaml",
            ".yml": "yaml",
            ".md": "markdown",
            ".html": "html",
            ".css": "css",
            ".toml": "toml",
            ".txt": "text",
            "": "text",
        }
        extension = Path(file_path).suffix.lower()
        language = lang_map.get(extension, "text")

        try:
            existing_pane = self.file_tabs.get_pane(pane_id)
            editor = existing_pane.query_one(TextArea)
            editor.load_text(text)
            editor.language = language
        except NoMatches:
            editor_id = f"editor_{self.file_tabs.tab_count}"
            editor = TextArea(text, id=editor_id, language=language)
            new_pane_widget = TabPane(Path(file_path).name, editor, id=pane_id)
            if not self.file_tabs.display:
                self.file_tabs.display = True
            await self.file_tabs.add_pane(new_pane_widget)

        self.file_tabs.active = pane_id
        self.toast(f"Editing {Path(file_path).name}", style="success", duration=1.5)

    async def open_text(self, name: str, text: str, language: str = "text") -> None:
        pane_id = f"text:{name}"
        try:
            existing_pane = self.file_tabs.get_pane(pane_id)
            editor = existing_pane.query_one(TextArea)
            editor.load_text(text)
            editor.language = language
        except NoMatches:
            editor = TextArea(text, language=language)
            new_pane = TabPane(name, editor, id=pane_id)
            if not self.file_tabs.display:
                self.file_tabs.display = True
            await self.file_tabs.add_pane(new_pane)
        self.file_tabs.active = pane_id

    async def open_git_oid(self, oid: str) -> None:
        try:
            from peagen.core.mirror_core import open_repo

            vcs = open_repo(".")
            content = vcs.object_pretty(oid)
        except Exception as exc:
            self.toast(f"Cannot load OID {oid}: {exc}", style="error")
            return
        await self.open_text(oid, content)

    async def _show_reconnect(self, message: str) -> None:
        if self._reconnect_screen:
            return
        self._reconnect_screen = ReconnectScreen(message, self.retry_connection)
        await self.push_screen(self._reconnect_screen)

    async def _dismiss_reconnect(self) -> None:
        if self._reconnect_screen:
            await self._reconnect_screen.dismiss()
            self._reconnect_screen = None


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Peagen dashboard")
    parser.add_argument("--gateway-url", default="http://localhost:8000")
    args = parser.parse_args()
    QueueDashboardApp(gateway_url=args.gateway_url).run()
