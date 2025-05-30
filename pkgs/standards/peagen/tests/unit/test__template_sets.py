import random; random.seed(0xA11A)
import subprocess
import importlib.metadata as im
import pytest

from peagen._template_sets import install_template_sets


@pytest.mark.unit
def test_install_local(monkeypatch, tmp_path):
    calls = []
    monkeypatch.setattr(subprocess, "check_call", lambda cmd: calls.append(cmd))
    monkeypatch.setattr(im, "version", lambda name: "1.0")
    specs = [{"name": "pkg", "type": "local", "target": str(tmp_path)}]
    res = install_template_sets(specs)
    assert res[0]["name"] == "pkg"
    assert calls
