import pytest
from peagen.tui import app as tui_app
from peagen.tui.app import QueueDashboardApp
from textual.widgets import DataTable


class DummyTable(DataTable):
    @property
    def cursor_row(self):
        return 0

    @property
    def cursor_column(self):
        return 0

    def get_cell(self, row, col):
        return "cell"

    def get_cell_at(self, coordinate):
        return "cell"


def make_property(value):
    return property(lambda self: value)


@pytest.mark.unit
def test_action_copy_selection_datatable(monkeypatch):
    captured = {}

    def fake_copy(text):
        captured["text"] = text

    monkeypatch.setattr(tui_app, "clipboard_copy", fake_copy)
    table = DummyTable()
    monkeypatch.setattr(QueueDashboardApp, "focused", make_property(table))

    app = QueueDashboardApp()
    app.action_copy_selection()

    assert captured["text"] == "cell"


@pytest.mark.unit
def test_action_copy_selection_input(monkeypatch):
    captured = {}

    def fake_copy(text):
        captured["text"] = text

    monkeypatch.setattr(tui_app, "clipboard_copy", fake_copy)

    class DummyInput:
        selected_text = "sel"
        value = "val"

    dummy = DummyInput()
    monkeypatch.setattr(QueueDashboardApp, "focused", make_property(dummy))

    app = QueueDashboardApp()
    app.action_copy_selection()

    assert captured["text"] == "sel"


@pytest.mark.unit
def test_action_paste_clipboard_input(monkeypatch):
    def fake_paste():
        return "stuff"

    monkeypatch.setattr(tui_app, "clipboard_paste", fake_paste)

    class DummyInput:
        def __init__(self):
            self.inserted = None

        def insert_text_at_cursor(self, text):
            self.inserted = text

    dummy = DummyInput()
    monkeypatch.setattr(QueueDashboardApp, "focused", make_property(dummy))

    app = QueueDashboardApp()
    app.action_paste_clipboard()

    assert dummy.inserted == "stuff"


@pytest.mark.unit
def test_action_paste_clipboard_textarea(monkeypatch):
    def fake_paste():
        return "more"

    monkeypatch.setattr(tui_app, "clipboard_paste", fake_paste)

    class DummyTA:
        def __init__(self):
            self.inserted = None

        def insert(self, text):
            self.inserted = text

    dummy = DummyTA()
    monkeypatch.setattr(QueueDashboardApp, "focused", make_property(dummy))

    app = QueueDashboardApp()
    app.action_paste_clipboard()

    assert dummy.inserted == "more"
