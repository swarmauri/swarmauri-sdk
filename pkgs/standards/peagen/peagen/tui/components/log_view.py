from pathlib import Path

from textual.widgets import DataTable


class LogView(DataTable):
    def __init__(self, error_mode=False):
        super().__init__()
        self.error_mode = error_mode

    def on_mount(self):
        self.add_columns("Time", "Message", "File")
        self.add_row("12:01", "Something happened", self.make_link("README.md"))
        if self.error_mode:
            self.add_row("12:05", "[ERROR] crash", self.make_link("app/error.py"))

    def make_link(self, file_path):
        abs_path = Path(file_path).resolve()
        return f"[link=file://{abs_path}]{file_path}[/link]"
