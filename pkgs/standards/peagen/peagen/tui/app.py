# queue_dash.py – run with  `python -m queue_dash`
"""Textual dashboard for Peagen.

🚧 editing template-sets not implemented yet
"""

# 🚧 editing template-sets not implemented yet

from __future__ import annotations

import asyncio
import itertools
import random
from datetime import datetime
from pathlib import Path
from typing import Dict
from urllib.parse import urlparse

from peagen.tui.fileops import download_remote, upload_remote
from peagen.tui.ws_client import TaskStreamClient

from rich.progress import ProgressBar

# ── imports ──────────────────────────────────────────────────────────
from textual import events
from textual.app import App, ComposeResult
from textual.containers import VerticalScroll
from textual.reactive import reactive
from textual.widgets import (
    DataTable,
    Footer,
    Header,
    Static,
    TabbedContent,
    TabPane,
    TextArea,
)

from peagen.tui.components.tree_view import FileTree


# ───────────────────────────────────  Fake backend  ────────────────────────────────────
class Task:
    _ids = itertools.count(1)

    def __init__(self, queue: str):
        self.id = next(self._ids)
        self.queue = queue
        self.total = random.randint(50, 120)
        self.done = 0
        self.status = "running"  # running / done / failed
        self.error_file: Path | None = None

    def step(self):
        if self.status != "running":
            return
        self.done += random.randint(2, 6)
        if self.done >= self.total:
            self.done = self.total
            if random.random() < 0.12:
                self.status = "failed"
                self.error_file = Path(f"./logs/task_{self.id}.log")
            else:
                self.status = "done"

    @property
    def percent(self) -> float:
        return self.done / self.total * 100


class FakeBackend:
    def __init__(self):
        self.tasks: list[Task] = []
        self.workers: Dict[str, datetime] = {
            f"worker-{n}": datetime.utcnow() for n in range(2)
        }

    async def poll(self):
        while True:
            await asyncio.sleep(0.2)
            if random.random() < 0.25:
                self.tasks.append(Task("default"))
            for t in self.tasks:
                t.step()
            for w in self.workers:
                if random.random() < 0.1:
                    self.workers[w] = datetime.utcnow()
            self.tasks[:] = [
                t
                for t in self.tasks
                if not (t.status != "running" and random.random() < 0.04)
            ]


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
        ("1", "switch('overview')", "Overview"),
        ("2", "switch('tasks')", "Tasks"),
        ("3", "switch('errors')", "Errors"),
        ("4", "switch('files')", "Files"),
        ("5", "switch('editor')", "Editor"),
        ("ctrl+s", "save_file", "Save"),
        ("q", "quit", "Quit"),
    ]

    def __init__(self, gateway_url: str = "http://localhost:8000") -> None:
        super().__init__()
        ws_url = gateway_url.replace("http", "ws").rstrip("/") + "/ws/tasks"
        self.client = TaskStreamClient(ws_url)
        self.backend = FakeBackend()

    # reactive counters for quick overview
    queue_len = reactive(0)
    done_len = reactive(0)
    fail_len = reactive(0)
    worker_len = reactive(0)

    # ── life-cycle ──────────────────────────────────────────────────────────
    async def on_mount(self):
        self.run_worker(self.backend.poll(), exclusive=True)
        self.run_worker(self.client.listen(), exclusive=True)
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
        self.overview_box = Static(id="stats")
        self.file_tree = FileTree("tree", id="file_tree")
        self.tasks_table = DataTable(id="tasks_table")
        self.tasks_table.add_columns("ID", "Status", "Progress")

        self.err_table = DataTable(id="err_table")
        self.err_table.add_columns("Task", "Log")
        # after creating err_table
        self.err_table.cursor_type = "cell"  # ensure per-cell click events
        self.err_table.focus()  # mouse-click instantly focuses table

        self.code_editor = TextArea(id="code_editor")

        with TabbedContent(initial="overview"):
            yield TabPane("Overview", VerticalScroll(self.overview_box), id="overview")
            yield TabPane("Tasks", self.tasks_table, id="tasks")
            yield TabPane("Errors", self.err_table, id="errors")
            yield TabPane("Files", self.file_tree, id="files")
            yield TabPane("Editor", self.code_editor, id="editor")

        yield Footer()

    # ── key binding helpers ────────────────────────────────────────────────
    def action_switch(self, tab_id: str) -> None:
        self.query_one(TabbedContent).active = tab_id

    # Ctrl-S in the editor
    def action_save_file(self) -> None:
        if not hasattr(self, "_current_file"):
            self.toast("No file loaded.", style="yellow")
            return
        if getattr(self, "_remote_info", None):
            adapter, key, tmp = self._remote_info
            tmp.write_text(self.code_editor.value, encoding="utf-8")
            try:
                upload_remote(adapter, key, tmp)
                self.toast("Uploaded remote file", style="green")
            except Exception as exc:
                self.toast(f"Upload failed: {exc}", style="red")
        else:
            try:
                Path(self._current_file).write_text(
                    self.code_editor.value, encoding="utf-8"
                )
                self.toast(f"Saved {self._current_file}", style="green")
            except Exception as exc:
                self.toast(f"Save failed: {exc}", style="red")

    # ── periodic refresh logic ─────────────────────────────────────────────
    def refresh_data(self) -> None:
        tasks = list(self.client.tasks.values()) or self.backend.tasks
        workers = self.backend.workers

        # 1 – overview
        self.queue_len = sum(1 for t in tasks if getattr(t, "status", t.get("status")) == "running")
        self.done_len = sum(1 for t in tasks if getattr(t, "status", t.get("status")) == "done")
        self.fail_len = sum(1 for t in tasks if getattr(t, "status", t.get("status")) == "failed")
        self.worker_len = len(workers)
        self.overview_box.update(
            f"[bold cyan]Active workers:[/bold cyan] {self.worker_len}\n"
            f"[bold cyan]Tasks running:[/bold cyan] {self.queue_len}\n"
            f"[bold cyan]Completed:[/bold cyan]     {self.done_len}\n"
            f"[bold cyan]Failed:[/bold cyan]        {self.fail_len}\n"
        )

        # 2 – tasks table
        running = [t for t in tasks if getattr(t, "status", t.get("status")) == "running"]
        visible = set(self.tasks_table.rows.keys())
        for t in running:
            tid = getattr(t, "id", t.get("id"))
            status = getattr(t, "status", t.get("status"))
            pct = getattr(t, "percent", None)
            if pct is None:
                done = getattr(t, "done", t.get("done", 0))
                total = getattr(t, "total", t.get("total", 100))
                pct = done / total * 100 if total else 0
            if str(tid) not in visible:
                self.tasks_table.add_row(
                    str(tid),
                    status,
                    ProgressBar(total=100, completed=pct),
                    key=str(tid),
                )
            else:
                ...
                # # only progress cell needs refresh
                # self.tasks_table.update_cell(
                #     str(t.id), "Progress",
                #     ProgressBar(total=100, completed=t.percent),
                # )
        # purge finished rows
        for key in list(self.tasks_table.rows.keys()):
            if all(
                str(getattr(t, "id", t.get("id"))) != key
                or getattr(t, "status", t.get("status")) != "running"
                for t in tasks
            ):
                self.tasks_table.remove_row(key)

        # 3 – error table
        if self.fail_len:
            self.err_table.clear()
            for t in (t for t in tasks if getattr(t, "status", t.get("status")) == "failed"):
                err_file = getattr(t, "error_file", t.get("error_file"))
                link = f"[link=file://{err_file}]open[/link]" if err_file else ""
                tid = getattr(t, "id", t.get("id"))
                self.err_table.add_row(str(tid), link)

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

        self.code_editor.load_text(text)
        self.code_editor.language = "python"

        self.action_switch("editor")
        self.toast(f"Editing {file_path}", style="success", duration=1.5)


# ────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    QueueDashboardApp().run()
