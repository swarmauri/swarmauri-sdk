import types
import pytest
from typer.testing import CliRunner

from peagen.cli import app
from peagen.commands.plugins import plugins_app


@pytest.mark.unit
def test_help_lists_plugin_command():
    runner = CliRunner()
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "plugin" in result.output


@pytest.mark.unit
def test_plugin_list(monkeypatch):
    runner = CliRunner()

    class DummyEP:
        def __init__(self, name, value, group):
            self.name = name
            self.value = value
            self.group = group
            self.dist = types.SimpleNamespace(metadata={"Name": "dummy"})

    def fake_eps(group=None):
        if group == "peagen.storage_adapters":
            return [DummyEP("example", "pkg:Cls", group)]
        return []

    monkeypatch.setattr("importlib.metadata.entry_points", fake_eps)

    result = runner.invoke(plugins_app, ["list"])
    assert result.exit_code == 0
    assert "example" in result.output
