# queue_dash.py – run with  `python -m queue_dash`
"""Textual dashboard for Peagen.

🚧 editing template-sets not implemented yet
"""

# 🚧 editing template-sets not implemented yet

from __future__ import annotations

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List
from urllib.parse import urlparse
import subprocess
import sys

from peagen.tui.fileops import download_remote, upload_remote
from peagen.tui.ws_client import TaskStreamClient
from textual import events
from textual.app import App, ComposeResult
from textual.reactive import reactive
from textual.widgets import (
    DataTable,
    Header,
    Input,
    TabbedContent,
    TabPane,
    TextArea,
)
from textual.containers import Vertical
from peagen.tui.components import (
    DashboardFooter,
    FileTree,
    TemplatesView,
    WorkersView,
    ReconnectScreen,
)

import httpx


def clipboard_copy(text: str) -> None:
    """Write text to the system clipboard."""

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
    """Return the current system clipboard contents."""

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
    """Return an ISO timestamp regardless of input type."""
    if ts is None:
        return ""
    try:
        if isinstance(ts, str):
            return (
                datetime.fromisoformat(ts.replace("Z", "+00:00")).isoformat(timespec="seconds")
            )
        return datetime.utcfromtimestamp(float(ts)).isoformat(timespec="seconds")
    except Exception:
        return ""


class RemoteBackend:
    """Query the gateway for tasks and workers."""

    def __init__(self, gateway_url: str) -> None:
        self.rpc_url = gateway_url.rstrip("/") + "/rpc"
        self.http = httpx.AsyncClient(timeout=10.0)
        self.tasks: List[dict] = []
        self.workers: Dict[str, dict] = {}
        self.last_error: str | None = None

    async def refresh(self) -> bool:
        """Update cached tasks and workers.

        Returns:
            bool: ``True`` if the refresh succeeded, ``False`` otherwise.
        """

        try:
            await asyncio.gather(self.fetch_tasks(), self.fetch_workers())
        except Exception as exc:  # noqa: BLE001
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
            # attempt to decode JSON-encoded fields
            for k, v in list(info.items()):
                if isinstance(v, str) and (v.startswith("{") or v.startswith("[")):
                    try:
                        info[k] = json.loads(v)
                    except Exception:
                        pass
            workers[info["id"]] = info

        self.workers = workers


# ───────────────────────────────────  Dashboard app  ────────────────────────────────────
class QueueDashboardApp(App):
    CSS = """
    TabPane#editor {
        height: 1fr;            /* let the pane claim vertical space      */
        width:  1fr;            /* (optional) stretch to full width       */
    }

    TextArea#code_editor {
        height: 1fr;            /* fill the pane completely               */
        width:  1fr;
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
        ("f", "toggle_filter_input", "Filter"),
        ("escape", "clear_filters", "Clear Filters"),
        ("q", "quit", "Quit"),
    ]

    def __init__(self, gateway_url: str = "http://localhost:8000") -> None:
        super().__init__()
        ws_url = gateway_url.replace("http", "ws").rstrip("/") + "/ws/tasks"
        self.client = TaskStreamClient(ws_url)
        self.backend = RemoteBackend(gateway_url)
        self.sort_key = "time"
        self.filter_pool: str | None = None
        self.filter_status: str | None = None
        self.filter_action: str | None = None
        self.filter_label: str | None = None
        self.collapsed: set[str] = set()
        self._reconnect_screen: ReconnectScreen | None = None

    # reactive counters for quick overview
    queue_len = reactive(0)
    done_len = reactive(0)
    fail_len = reactive(0)
    worker_len = reactive(0)

    # ── life-cycle ──────────────────────────────────────────────────────────
    async def on_mount(self):
        self.run_worker(self.client.listen(), exclusive=True)
        self.set_interval(1.0, self._refresh_backend)
        self.set_interval(0.3, self.refresh_data)

    async def _refresh_backend(self) -> None:
        """Fetch latest data or prompt reconnect on failure."""

        if self._reconnect_screen:
            return
        ok = await self.backend.refresh()
        if not ok and not self._reconnect_screen:
            await self._show_reconnect(self.backend.last_error or "Connection failed")
        elif ok and self._reconnect_screen:
            await self._dismiss_reconnect()

    async def on_open_url(self, event: events.OpenURL) -> None:
        """Catch clicks on [link=file://…] and open them in the editor tab
        instead of the system browser."""
        if event.url.startswith("file://"):
            event.prevent_default()  # stop Textual’s built-in handler
            event.stop()  # don’t bubble any further
            await self.open_editor(event.url.removeprefix("file://"))

    async def on_file_tree_file_selected(  # ← snake-case of the message
        self,
        message: FileTree.FileSelected,
    ) -> None:
        """Open the clicked file in the Editor tab."""
        message.stop()  # suppress any default handling
        await self.open_editor(message.path.as_posix())

    # ----------------------------------------------------------------------—
    # Back-compat shim: use App.notify if it exists, otherwise fall back to log()
    def toast(
        self, message: str, *, style: str = "information", duration: float | None = 2.0
    ) -> None:
        if hasattr(self, "notify"):  # Textual ≥ 0.30
            self.notify(message, severity=style, timeout=duration)
        else:  # very old Textual
            self.log(f"[{style.upper()}] {message}")

    def compose(self) -> ComposeResult:
        yield Header()

        # widgets whose content we mutate later
        self.workers_view = WorkersView(id="workers_view")
        self.file_tree = FileTree("tree", id="file_tree")
        self.templates_tree = TemplatesView(id="templates_tree")
        self.tasks_table = DataTable(id="tasks_table")
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
        self.tasks_table.focus()

        self.err_table = DataTable(id="err_table")
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
        # after creating err_table
        self.err_table.cursor_type = "cell"  # ensure per-cell click events
        self.err_table.focus()  # mouse-click instantly focuses table

        self.code_editor = TextArea(id="code_editor")
        self.file_tabs = TabbedContent(id="file_tabs")
        self.file_tabs.display = False
        self.filter_input = Input(placeholder="pool=default status=running", id="filter_input")
        self.filter_input.display = False

        with Vertical():
            yield self.filter_input
            with TabbedContent(initial="pools"):
                yield TabPane("Pools", self.workers_view, id="pools")
                yield TabPane("Tasks", self.tasks_table, id="tasks")
                yield TabPane("Errors", self.err_table, id="errors")
                yield TabPane("Artifacts", self.file_tree, id="artifacts")
                yield TabPane("Templates", self.templates_tree, id="templates")

        yield self.file_tabs
        yield DashboardFooter()

    # ── key binding helpers ────────────────────────────────────────────────
    def action_switch(self, tab_id: str) -> None:
        self.query_one(TabbedContent).active = tab_id

    # Ctrl-S in the editor
    def action_save_file(self) -> None:
        if not hasattr(self, "_current_file"):
            self.toast("No file loaded.", style="yellow")
            return
        editor = self.file_tabs.active_pane.query_one(TextArea)
        if getattr(self, "_remote_info", None):
            adapter, key, tmp = self._remote_info
            tmp.write_text(editor.value, encoding="utf-8")
            try:
                upload_remote(adapter, key, tmp)
                self.toast("Uploaded remote file", style="green")
            except Exception as exc:
                self.toast(f"Upload failed: {exc}", style="red")
        else:
            try:
                Path(self._current_file).write_text(editor.value, encoding="utf-8")
                self.toast(f"Saved {self._current_file}", style="green")
            except Exception as exc:
                self.toast(f"Save failed: {exc}", style="red")

    def action_toggle_children(self) -> None:
        row = self.tasks_table.cursor_row
        if row is None:
            return

        # ``DataTable``'s API changed across Textual versions.  Newer
        # releases expose ``get_row_key`` while older versions require
        # accessing the row object directly.  Support both styles so the
        # dashboard works regardless of the installed Textual release.
        if hasattr(self.tasks_table, "get_row_key"):
            row_key = self.tasks_table.get_row_key(row)
        else:  # fallback for older versions
            row_obj = (
                self.tasks_table.get_row_at(row)
                if hasattr(self.tasks_table, "get_row_at")
                else None
            )
            row_key = getattr(row_obj, "key", None) if row_obj else None

        if row_key is None:
            return

        row_key = str(row_key)

        if row_key in self.collapsed:
            self.collapsed.remove(row_key)
        else:
            self.collapsed.add(row_key)
        self.refresh_data()

    SORT_KEYS = ["time", "pool", "status", "action", "label", "duration"]

    def action_cycle_sort(self) -> None:
        try:
            idx = self.SORT_KEYS.index(self.sort_key)
        except ValueError:  # pragma: no cover - unknown sort_key
            idx = 0
        self.sort_key = self.SORT_KEYS[(idx + 1) % len(self.SORT_KEYS)]
        self.toast(f"Sorting by {self.sort_key}", duration=1.0)
        self.refresh_data()

    def action_filter_by_cell(self) -> None:
        row = self.tasks_table.cursor_row
        col = self.tasks_table.cursor_column
        if row is None or col is None:
            return

        # get cell value
        if hasattr(self.tasks_table, "get_cell_at"):
            value = self.tasks_table.get_cell_at(row, col)
        else:
            value = self.tasks_table.get_cell(
                row, col
            )  # pragma: no cover - old textual

        col_label = self.tasks_table.columns[col].label
        if col_label == "Pool":
            self.filter_pool = None if self.filter_pool == value else str(value)
        elif col_label == "Status":
            self.filter_status = None if self.filter_status == value else str(value)
        elif col_label == "Action":
            self.filter_action = None if self.filter_action == value else str(value)
        elif col_label == "Labels":
            lbl = str(value).split(",")[0] if value else ""
            self.filter_label = None if self.filter_label == lbl else lbl
        self.refresh_data()

    def action_toggle_filter_input(self) -> None:
        """Show or hide the filter input bar."""

        self.filter_input.display = not self.filter_input.display
        if self.filter_input.display:
            self.filter_input.value = ""
            self.filter_input.focus()

    def action_clear_filters(self) -> None:
        self.filter_pool = None
        self.filter_status = None
        self.filter_action = None
        self.filter_label = None
        self.filter_input.value = ""
        self.filter_input.display = False
        self.refresh_data()

    def action_copy_id(self) -> None:
        """Copy the text from the focused widget to the clipboard."""

        widget = self.focused
        text = ""
        if isinstance(widget, DataTable):
            row = widget.cursor_row
            col = widget.cursor_column
            if row is not None and col is not None:
                if hasattr(widget, "get_cell_at"):
                    value = widget.get_cell_at(row, col)
                else:  # pragma: no cover - old textual
                    value = widget.get_cell(row, col)
                text = str(value)
        elif isinstance(widget, (Input, TextArea)):
            text = getattr(widget, "selected_text", "") or getattr(widget, "value", "")
        if text:
            clipboard_copy(text)

    def action_paste_clipboard(self) -> None:
        """Paste clipboard text into the focused input widget."""

        widget = self.focused
        text = clipboard_paste()
        if isinstance(widget, Input):
            insert = getattr(widget, "insert_text_at_cursor", None)
            if insert:
                insert(text)
        elif isinstance(widget, TextArea):
            insert = getattr(widget, "insert", None) or getattr(widget, "insert_text_at_cursor", None)
            if insert:
                insert(text)

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Apply filters from the input bar."""

        if event.input is not self.filter_input:
            return
        text = event.value.strip()
        self.filter_pool = None
        self.filter_status = None
        self.filter_action = None
        self.filter_label = None
        for token in text.split():
            if "=" not in token:
                continue
            key, value = token.split("=", 1)
            if key == "pool":
                self.filter_pool = value
            elif key == "status":
                self.filter_status = value
            elif key == "action":
                self.filter_action = value
            elif key == "label":
                self.filter_label = value
        self.filter_input.display = False
        self.refresh_data()

    # ── periodic refresh logic ─────────────────────────────────────────────
    def refresh_data(self) -> None:
        tasks = list(self.client.tasks.values()) or self.backend.tasks

        # apply filters
        if self.filter_pool:
            tasks = [t for t in tasks if t.get("pool") == self.filter_pool]
        if self.filter_status:
            tasks = [t for t in tasks if t.get("status") == self.filter_status]
        if self.filter_action:
            tasks = [
                t
                for t in tasks
                if t.get("payload", {}).get("action") == self.filter_action
            ]
        if self.filter_label:
            tasks = [t for t in tasks if self.filter_label in t.get("labels", [])]

        # sort
        if self.sort_key:

            def _key(task):
                if self.sort_key == "action":
                    return task.get("payload", {}).get("action")
                if self.sort_key == "label":
                    return ",".join(task.get("labels", []))
                if self.sort_key == "duration":
                    return task.get("duration") or 0
                return task.get(self.sort_key)

            tasks.sort(key=lambda t: _key(t) or "")
        if self.client.workers:
            workers = {}
            for wid, data in self.client.workers.items():
                info = {**data}
                ts_raw = info.get("last_seen", datetime.utcnow().timestamp())
                try:
                    ts = float(ts_raw)
                except (TypeError, ValueError):
                    ts = datetime.utcnow().timestamp()
                info["last_seen"] = datetime.utcfromtimestamp(ts)
                workers[wid] = info
        else:
            workers = self.backend.workers

        # 1 – workers and counts
        if self.client.queues:
            self.queue_len = sum(self.client.queues.values())
        else:
            self.queue_len = sum(
                1 for t in tasks if getattr(t, "status", t.get("status")) == "running"
            )
        self.done_len = sum(
            1 for t in tasks if getattr(t, "status", t.get("status")) == "done"
        )
        self.fail_len = sum(
            1 for t in tasks if getattr(t, "status", t.get("status")) == "failed"
        )
        if self.filter_pool:
            workers = {
                wid: w
                for wid, w in workers.items()
                if w.get("pool") == self.filter_pool
            }
        self.worker_len = len(workers)
        self.workers_view.update_workers(workers)

        # 2 – tasks table
        row = self.tasks_table.cursor_row
        column = self.tasks_table.cursor_column
        self.tasks_table.clear()
        seen: set[str] = set()
        for t in tasks:
            tid = t.get("id")
            if tid in seen:
                continue
            pool = t.get("pool", "")
            status = t.get("status")
            action = t.get("payload", {}).get("action", "")
            labels = ",".join(t.get("labels", []))
            started = t.get("started_at")
            finished = t.get("finished_at")
            duration = t.get("duration")
            ts = t.get("time", "")
            prefix = ""
            children = t.get("result", {}).get("children")
            if children:
                prefix = "- " if tid not in self.collapsed else "+ "
            self.tasks_table.add_row(
                f"{prefix}{tid}",
                pool,
                status,
                action,
                labels,
                _format_ts(started),
                _format_ts(finished),
                str(duration) if duration is not None else "",
                key=str(tid),
            )
            seen.add(tid)
            if children and tid not in self.collapsed:
                for cid in children:
                    child = next((c for c in tasks if c.get("id") == cid), None)
                    if child and cid not in seen:
                        c_labels = ",".join(child.get("labels", []))
                        c_start = child.get("started_at")
                        c_finish = child.get("finished_at")
                        c_dur = child.get("duration")
                        self.tasks_table.add_row(
                            f"  {cid}",
                            child.get("pool", ""),
                            child.get("status"),
                            child.get("payload", {}).get("action", ""),
                            c_labels,
                            _format_ts(c_start),
                            _format_ts(c_finish),
                            str(c_dur) if c_dur is not None else "",
                            key=str(cid),
                        )
                        seen.add(cid)

        # restore selection
        if row is not None and row < len(self.tasks_table.rows):
            self.tasks_table.cursor_coordinate = (row, column or 0)

        # 3 – error table
        if self.fail_len:
            err_row = self.err_table.cursor_row
            err_col = self.err_table.cursor_column
            self.err_table.clear()
            for t in (
                t for t in tasks if getattr(t, "status", t.get("status")) == "failed"
            ):
                err_file = getattr(t, "error_file", t.get("error_file"))
                link = f"[link=file://{err_file}]open[/link]" if err_file else ""
                tid = getattr(t, "id", t.get("id"))
                result = getattr(t, "result", t.get("result", {})) or {}
                err_msg = result.get("error", "")
                started = t.get("started_at")
                finished = t.get("finished_at")
                duration = t.get("duration")
                self.err_table.add_row(
                    str(tid),
                    t.get("pool", ""),
                    t.get("status"),
                    t.get("payload", {}).get("action", ""),
                    ",".join(t.get("labels", [])),
                    _format_ts(started),
                    _format_ts(finished),
                    str(duration) if duration is not None else "",
                    f"{err_msg} {link}".strip(),
                )
            if err_row is not None and err_row < len(self.err_table.rows):
                self.err_table.cursor_coordinate = (err_row, err_col or 0)

    # ── open selected file in editor instead of browser ────────────────────
    async def on_data_table_cell_selected(self, event: DataTable.CellSelected) -> None:
        if isinstance(event.value, str) and event.value.startswith("[link="):
            path = event.value.split("=", 1)[1].split("]", 1)[0]
            await self.open_editor(Path(path).as_posix())

    # ----------------------------------------------------------------------—
    async def open_editor(self, file_path: str) -> None:
        parsed = urlparse(file_path)
        if parsed.scheme and parsed.scheme != "file":
            try:
                tmp, adapter, key = download_remote(file_path)
            except Exception as exc:
                self.toast(f"Cannot download {file_path}: {exc}", style="error")
                return
            self._remote_info = (adapter, key, tmp)
            text = tmp.read_text(encoding="utf-8")
            self._current_file = tmp.as_posix()
        else:
            try:
                text = Path(file_path).read_text(encoding="utf-8")
            except Exception as exc:
                self.toast(f"Cannot open {file_path}: {exc}", style="error")
                return
            self._remote_info = None
            self._current_file = file_path

        pane_id = file_path
        if not self.file_tabs.get_child_by_id(pane_id):
            editor = TextArea(id=f"editor_{len(self.file_tabs.panes)}")
            editor.load_text(text)
            editor.language = "python"
            await self.file_tabs.add_pane(
                TabPane(Path(file_path).name, editor, id=pane_id)
            )
            self.file_tabs.display = True
        else:
            editor = self.file_tabs.query_one(f"#{pane_id} TextArea")
            editor.load_text(text)
        self.file_tabs.active = pane_id
        self.toast(f"Editing {file_path}", style="success", duration=1.5)

    # ------------------------------------------------------------------
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
        self.run_worker(self.client.listen(), exclusive=True)
        ok = await self.backend.refresh()
        if ok:
            await self._dismiss_reconnect()
        else:
            await self._show_reconnect(self.backend.last_error or "Connection failed")


# ────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Peagen dashboard")
    parser.add_argument("--gateway-url", default="http://localhost:8000")
    args = parser.parse_args()

    QueueDashboardApp(gateway_url=args.gateway_url).run()
