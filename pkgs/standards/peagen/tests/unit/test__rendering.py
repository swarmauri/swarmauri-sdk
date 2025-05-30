import random; random.seed(0xA11A)
import types
import pytest

from peagen._rendering import _render_copy_template, _render_generate_template


class DummyJ2:
    def __init__(self):
        self.template = None

    def set_template(self, path):
        self.template = str(path)

    def fill(self, ctx):
        return f"ok:{ctx['FILE']['NAME']}"


def _dummy_record(name="f.txt"):
    return {"FILE_NAME": name, "RENDERED_FILE_NAME": name}


@pytest.mark.unit
def test_render_copy(monkeypatch):
    j2 = DummyJ2()
    res = _render_copy_template(_dummy_record(), {"FILE": {"NAME": "x"}}, j2)
    assert res == "ok:x"
    assert "f.txt" in j2.template


@pytest.mark.unit
def test_render_generate(monkeypatch):
    j2 = DummyJ2()
    monkeypatch.setattr("peagen._external.call_external_agent", lambda *a, **k: "gen")
    res = _render_generate_template(_dummy_record(), {"FILE": {"NAME": "x"}}, "t.j2", j2)
    assert res == "gen"
