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

from peagen.tui.fileops import download_remote, upload_remote
from peagen.tui.ws_client import TaskStreamClient
from textual import events
from textual.app import App, ComposeResult
from textual.reactive import reactive
from textual.widgets import (
    DataTable,
    Header,
    TabbedContent,
    TabPane,
    TextArea,
)

from peagen.tui.components import (
    DashboardFooter,
    FileTree,
    TemplatesView,
    WorkersView,
)

import httpx


class RemoteBackend:
    """Query the gateway for tasks and workers."""

    def __init__(self, gateway_url: str) -> None:
        self.rpc_url = gateway_url.rstrip("/") + "/rpc"
        self.http = httpx.AsyncClient(timeout=10.0)
        self.tasks: List[dict] = []
        self.workers: Dict[str, dict] = {}

    async def refresh(self) -> None:
        await asyncio.gather(self.fetch_tasks(), self.fetch_workers())

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
        ("q", "quit", "Quit"),
    ]

    def __init__(
        self,
        gateway_url: str = "http://localhost:8000",
        *,
        sort_key: str | None = None,
        filter_pool: str | None = None,
        filter_status: str | None = None,
        filter_action: str | None = None,
        filter_label: str | None = None,
    ) -> None:
        super().__init__()
        ws_url = gateway_url.replace("http", "ws").rstrip("/") + "/ws/tasks"
        self.client = TaskStreamClient(ws_url)
        self.backend = RemoteBackend(gateway_url)
        self.sort_key = sort_key or "time"
        self.filter_pool = filter_pool
        self.filter_status = filter_status
        self.filter_action = filter_action
        self.filter_label = filter_label
        self.collapsed: set[str] = set()

    # reactive counters for quick overview
    queue_len = reactive(0)
    done_len = reactive(0)
    fail_len = reactive(0)
    worker_len = reactive(0)

    # ── life-cycle ──────────────────────────────────────────────────────────
    async def on_mount(self):
        self.run_worker(self.client.listen(), exclusive=True)
        self.set_interval(1.0, self.backend.refresh)
        self.set_interval(0.3, self.refresh_data)

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
        self.tasks_table.add_columns("ID", "Pool", "Status", "Action", "Labels", "Time")

        self.err_table = DataTable(id="err_table")
        self.err_table.add_columns("Task", "Log")
        # after creating err_table
        self.err_table.cursor_type = "cell"  # ensure per-cell click events
        self.err_table.focus()  # mouse-click instantly focuses table

        self.code_editor = TextArea(id="code_editor")
        self.file_tabs = TabbedContent(id="file_tabs")
        self.file_tabs.display = False

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
        row_key = self.tasks_table.get_row_key(row)
        if row_key in self.collapsed:
            self.collapsed.remove(row_key)
        else:
            self.collapsed.add(row_key)

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
            tasks = [
                t
                for t in tasks
                if self.filter_label in t.get("labels", [])
            ]

        # sort
        if self.sort_key:
            def _key(task):
                if self.sort_key == "action":
                    return task.get("payload", {}).get("action")
                if self.sort_key == "label":
                    return ",".join(task.get("labels", []))
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
        self.done_len = sum(1 for t in tasks if getattr(t, "status", t.get("status")) == "done")
        self.fail_len = sum(1 for t in tasks if getattr(t, "status", t.get("status")) == "failed")
        self.worker_len = len(workers)
        self.workers_view.update_workers(workers)

        # 2 – tasks table
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
                ts,
                key=str(tid),
            )
            seen.add(tid)
            if children and tid not in self.collapsed:
                for cid in children:
                    child = next((c for c in tasks if c.get("id") == cid), None)
                    if child and cid not in seen:
                        c_labels = ",".join(child.get("labels", []))
                        c_ts = child.get("time", "")
                        self.tasks_table.add_row(
                            f"  {cid}",
                            child.get("pool", ""),
                            child.get("status"),
                            child.get("payload", {}).get("action", ""),
                            c_labels,
                            c_ts,
                            key=str(cid),
                        )
                        seen.add(cid)

        # 3 – error table
        if self.fail_len:
            self.err_table.clear()
            for t in (t for t in tasks if getattr(t, "status", t.get("status")) == "failed"):
                err_file = getattr(t, "error_file", t.get("error_file"))
                link = f"[link=file://{err_file}]open[/link]" if err_file else ""
                tid = getattr(t, "id", t.get("id"))
                result = getattr(t, "result", t.get("result", {})) or {}
                err_msg = result.get("error", "")
                self.err_table.add_row(str(tid), f"{err_msg} {link}".strip())

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
            await self.file_tabs.add_pane(TabPane(Path(file_path).name, editor, id=pane_id))
            self.file_tabs.display = True
        else:
            editor = self.file_tabs.query_one(f"#{pane_id} TextArea")
            editor.load_text(text)
        self.file_tabs.active = pane_id
        self.toast(f"Editing {file_path}", style="success", duration=1.5)


# ────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Peagen dashboard")
    parser.add_argument("--gateway-url", default="http://localhost:8000")
    parser.add_argument("--sort", choices=["time", "pool", "status", "action", "label"], default="time")
    parser.add_argument("--filter-pool")
    parser.add_argument("--filter-status")
    parser.add_argument("--filter-action")
    parser.add_argument("--filter-label")
    args = parser.parse_args()

    QueueDashboardApp(
        gateway_url=args.gateway_url,
        sort_key=args.sort,
        filter_pool=args.filter_pool,
        filter_status=args.filter_status,
        filter_action=args.filter_action,
        filter_label=args.filter_label,
    ).run()
