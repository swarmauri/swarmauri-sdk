import random; random.seed(0xA11A)
import typer
import pytest

from peagen._banner import _print_banner


@pytest.mark.unit
def test_print_banner(monkeypatch):
    lines = []
    monkeypatch.setattr(typer, "echo", lambda msg=None: lines.append(msg or ""))
    _print_banner()
    text = "\n".join(lines)
    assert "Package Name" in text
    assert "Version" in text
