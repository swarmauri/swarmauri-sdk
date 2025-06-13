from __future__ import annotations

import asyncio
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List
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
    Label,  # Added Label
    Select,
    TabbedContent,
    TabPane,
    TextArea,
)

from peagen.tui.components import (
    DashboardFooter,
    FileTree,
    FilterBar,
    ReconnectScreen,
    TaskDetailScreen,
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

    async def refresh(self) -> bool:
        try:
            await asyncio.gather(self.fetch_tasks(), self.fetch_workers())
        except Exception as exc:
            self.last_error = str(exc)
            return False
        else:
            self.last_error = None
            return True

    async def fetch_tasks(self) -> None:
        payload = {
            "jsonrpc": "2.0",
            "id": "1",
            "method": "Pool.listTasks",
            "params": {"poolName": "default"},
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
        ("ctrl+c", "copy_id", "Copy"),
        ("ctrl+p", "paste_clipboard", "Paste"),
        ("s", "cycle_sort", "Sort"),
        ("escape", "clear_filters", "Clear Filters"),
        ("q", "quit", "Quit"),
    ]

    SORT_KEYS = ["time", "pool", "status", "action", "label", "duration"]

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
        self.filter_id: str | None = None
        self.filter_pool: str | None = None
        self.filter_status: str | None = None
        self.filter_action: str | None = None
        self.filter_label: str | None = None
        self.collapsed: set[str] = set()
        self._reconnect_screen: ReconnectScreen | None = None
        self._filter_debounce_timer = None
        self._current_file: str | None = None
        self._remote_info: tuple | None = None

    async def on_mount(self):
        self.run_worker(
            self.client.listen(), exclusive=True, group="websocket_listener"
        )
        self.set_interval(1.0, self._refresh_backend_and_ui)
        self.trigger_data_processing()

    async def _refresh_backend_and_ui(self) -> None:
        if self._reconnect_screen:
            return
        ok = await self.backend.refresh()
        if not ok and not self._reconnect_screen:
            await self._show_reconnect(self.backend.last_error or "Connection failed")
        elif ok and self._reconnect_screen:
            await self._dismiss_reconnect()
        self.trigger_data_processing(debounce=False)

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

    async def async_process_and_update_data(self) -> None:
        all_tasks_from_client = list(self.client.tasks.values())
        all_tasks_from_backend = list(self.backend.tasks)
        combined_tasks_dict: Dict[str, Any] = {
            task.get("id"): task for task in all_tasks_from_backend
        }
        for task in all_tasks_from_client:
            combined_tasks_dict[task.get("id")] = task
        all_tasks = list(combined_tasks_dict.values())

        current_filter_criteria = {
            "id": self.filter_id,
            "pool": self.filter_pool,
            "status": self.filter_status,
            "action": self.filter_action,
            "label": self.filter_label,
            "sort_key": self.sort_key,
            "collapsed": self.collapsed.copy(),
        }
        processed_data = self._perform_filtering_and_sorting(
            all_tasks, current_filter_criteria
        )
        self.call_later(self._update_ui_with_processed_data, processed_data, all_tasks)

    def _perform_filtering_and_sorting(self, tasks_input: list, criteria: dict) -> dict:
        tasks = list(tasks_input)

        if criteria.get("id"):
            tasks = [t for t in tasks if str(t.get("id")) == criteria["id"]]
        if criteria.get("pool"):
            tasks = [t for t in tasks if t.get("pool") == criteria["pool"]]
        if criteria.get("status"):
            tasks = [t for t in tasks if t.get("status") == criteria["status"]]
        if criteria.get("action"):
            tasks = [
                t
                for t in tasks
                if t.get("payload", {}).get("action") == criteria["action"]
            ]
        if criteria.get("label"):
            tasks = [t for t in tasks if criteria["label"] in t.get("labels", [])]

        sort_key = criteria.get("sort_key")
        if sort_key:

            def _key_func(task_item):
                if sort_key == "action":
                    return task_item.get("payload", {}).get("action")
                if sort_key == "label":
                    return ",".join(task_item.get("labels", []))
                if sort_key == "duration":
                    return task_item.get("duration") or 0
                if sort_key == "time":
                    return (
                        task_item.get("started_at") or task_item.get("finished_at") or 0
                    )
                return task_item.get(sort_key)

            tasks.sort(key=lambda t: (_key_func(t) is None, _key_func(t)))

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

        return {
            "tasks_to_display": tasks,
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

        if hasattr(self, "workers_view"):
            self.workers_view.update_workers(workers_data)

        if hasattr(self, "filter_bar"):
            self.filter_bar.update_options(all_tasks_for_options)

        if hasattr(self, "tasks_table"):
            current_cursor_row = self.tasks_table.cursor_row
            current_cursor_column = self.tasks_table.cursor_column
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
                    prefix = "- " if task_id not in self.collapsed else "+ "

                self.tasks_table.add_row(
                    f"{prefix}{_truncate_id(task_id)}",
                    t_data.get("pool", ""),
                    t_data.get("status", ""),
                    t_data.get("payload", {}).get("action", ""),
                    ",".join(t_data.get("labels", [])),
                    _format_ts(t_data.get("started_at")),
                    _format_ts(t_data.get("finished_at")),
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
                                child_task.get("payload", {}).get("action", ""),
                                ",".join(child_task.get("labels", [])),
                                _format_ts(child_task.get("started_at")),
                                _format_ts(child_task.get("finished_at")),
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

        if hasattr(self, "err_table"):
            current_err_cursor_row = self.err_table.cursor_row
            current_err_cursor_column = self.err_table.cursor_column
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
                        t_data.get("payload", {}).get("action", ""),
                        ",".join(t_data.get("labels", [])),
                        _format_ts(t_data.get("started_at")),
                        _format_ts(t_data.get("finished_at")),
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

    async def on_open_url(self, event: events.OpenURL) -> None:
        if event.url.startswith("file://"):
            event.prevent_default()
            event.stop()
            await self.open_editor(event.url.removeprefix("file://"))

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
            "Duration",
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
            "Duration",
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
        yield DashboardFooter()
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

    def action_copy_id(self) -> None:
        widget = self.focused
        text = ""
        if isinstance(widget, DataTable):
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
        if text:
            clipboard_copy(text)

    def action_paste_clipboard(self) -> None:
        widget = self.focused
        text_to_paste = clipboard_paste()
        if isinstance(widget, TextArea):
            widget.insert_text_at_cursor(text_to_paste)

    async def on_data_table_cell_selected(self, event: DataTable.CellSelected) -> None:
        if isinstance(event.value, str) and event.value.startswith("[link="):
            path_str = event.value.split("=", 1)[1].split("]", 1)[0]
            await self.open_editor(Path(path_str).as_posix())
            return

        # Selection events no longer open task details automatically.
        return

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

    async def _show_reconnect(self, message: str) -> None:
        if self._reconnect_screen:
            return
        self._reconnect_screen = ReconnectScreen(message, self.retry_connection)
        await self.push_screen(self._reconnect_screen)

    async def _dismiss_reconnect(self) -> None:
        if self._reconnect_screen:
            await self._reconnect_screen.dismiss()
            self._reconnect_screen = None

    async def retry_connection(self) -> None:
        self.run_worker(
            self.client.listen(), exclusive=True, group="websocket_listener_retry"
        )
        ok = await self.backend.refresh()
        if ok:
            await self._dismiss_reconnect()
        else:
            if self._reconnect_screen:
                self._reconnect_screen.message = (
                    self.backend.last_error or "Connection failed"
                )
            else:
                await self._show_reconnect(
                    self.backend.last_error or "Connection failed"
                )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Peagen dashboard")
    parser.add_argument("--gateway-url", default="http://localhost:8000")
    args = parser.parse_args()
    QueueDashboardApp(gateway_url=args.gateway_url).run()
