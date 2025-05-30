import random; random.seed(0xA11A)
import os
import pytest

from peagen._processing import (
    _save_file,
    _create_context,
    _process_file,
)


class DummyJ2:
    def __init__(self):
        self.tmpl = None

    def set_template(self, p):
        self.tmpl = p

    def fill(self, ctx):
        return "content"


@pytest.mark.unit
def test_save_file(tmp_path):
    _save_file("data", "a/b.txt", workspace_root=tmp_path)
    assert (tmp_path / "a" / "b.txt").read_text() == "data"


@pytest.mark.unit
def test_create_context():
    rec = {"RENDERED_FILE_NAME": "f", "PROJECT_NAME": "P", "PACKAGE_NAME": "pkg", "MODULE_NAME": "m"}
    proj = {"NAME": "P", "PACKAGES": [{"NAME": "pkg", "MODULES": [{"NAME": "m"}]}]}
    ctx = _create_context(rec, proj)
    assert ctx["PROJ"]["NAME"] == "P"
    assert ctx["PKG"]["NAME"] == "pkg"
    assert ctx["MOD"]["NAME"] == "m"


@pytest.mark.unit
def test_process_file_copy(monkeypatch, tmp_path):
    rec = {"RENDERED_FILE_NAME": "x.txt", "PROCESS_TYPE": "COPY", "FILE_NAME": "foo"}
    monkeypatch.setattr("peagen._rendering._render_copy_template", lambda *a, **k: "ok")
    _process_file(rec, {}, tmp_path, {}, DummyJ2(), workspace_root=tmp_path)
    assert (tmp_path / "x.txt").exists()


@pytest.mark.unit
def test_process_file_generate(monkeypatch, tmp_path):
    rec = {
        "RENDERED_FILE_NAME": "y.txt",
        "PROCESS_TYPE": "GENERATE",
        "AGENT_PROMPT_TEMPLATE": "p.j2",
    }
    monkeypatch.setattr("peagen._rendering._render_generate_template", lambda *a, **k: "ok")
    _process_file(rec, {}, str(tmp_path), {}, DummyJ2(), workspace_root=tmp_path)
    assert (tmp_path / "y.txt").exists()


@pytest.mark.unit
def test_process_file_unknown(tmp_path):
    rec = {"RENDERED_FILE_NAME": "z", "PROCESS_TYPE": "WHAT"}
    assert not _process_file(rec, {}, str(tmp_path), {}, DummyJ2(), workspace_root=tmp_path)
