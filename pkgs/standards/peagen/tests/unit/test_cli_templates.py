import pytest
from typer.testing import CliRunner

from peagen.cli.commands.templates import local_template_sets_app
from peagen.core import templates_core


@pytest.mark.unit
def test_templates_list_reports_sets(tmp_path, monkeypatch):
    base = tmp_path / "templates"
    (base / "alpha").mkdir(parents=True)
    (base / "beta").mkdir()
    monkeypatch.setattr(templates_core, "_namespace_dirs", lambda: [base])
    monkeypatch.setattr(templates_core, "registry", {})

    def fake_run_handler(args):
        assert args == {"operation": "list"}
        return templates_core.list_template_sets()

    monkeypatch.setattr("peagen.cli.commands.templates._run_handler", fake_run_handler)
    runner = CliRunner()
    result = runner.invoke(local_template_sets_app, ["list"])
    assert result.exit_code == 0
    assert "alpha" in result.stdout
    assert "beta" in result.stdout
    assert "Total: 2 set(s)" in result.stdout


@pytest.mark.unit
def test_templates_list_handles_empty(tmp_path, monkeypatch):
    base = tmp_path / "templates"
    base.mkdir(parents=True)
    monkeypatch.setattr(templates_core, "_namespace_dirs", lambda: [base])
    monkeypatch.setattr(templates_core, "registry", {})

    def fake_run_handler(args):
        return templates_core.list_template_sets()

    monkeypatch.setattr("peagen.cli.commands.templates._run_handler", fake_run_handler)
    runner = CliRunner()
    result = runner.invoke(local_template_sets_app, ["list"])
    assert result.exit_code == 1
    assert "No template-sets found" in result.stdout


@pytest.mark.unit
def test_templates_show_displays_contents(tmp_path, monkeypatch):
    base = tmp_path / "templates"
    file_dir = base / "alpha"
    file_dir.mkdir(parents=True)
    (file_dir / "file.txt").write_text("data")
    monkeypatch.setattr(templates_core, "_namespace_dirs", lambda: [base])
    monkeypatch.setattr(templates_core, "registry", {})

    def fake_run_handler(args):
        assert args["operation"] == "show"
        return templates_core.show_template_set(args["name"])

    monkeypatch.setattr("peagen.cli.commands.templates._run_handler", fake_run_handler)
    runner = CliRunner()
    result = runner.invoke(local_template_sets_app, ["show", "alpha"])
    assert result.exit_code == 0
    assert f"Location:    {file_dir}" in result.stdout
    assert "file.txt" in result.stdout


@pytest.mark.unit
def test_templates_show_errors_on_missing(tmp_path, monkeypatch):
    base = tmp_path / "templates"
    base.mkdir(parents=True)
    monkeypatch.setattr(templates_core, "_namespace_dirs", lambda: [base])
    monkeypatch.setattr(templates_core, "registry", {})

    def fake_run_handler(args):
        return templates_core.show_template_set(args["name"])

    monkeypatch.setattr("peagen.cli.commands.templates._run_handler", fake_run_handler)
    runner = CliRunner()
    result = runner.invoke(local_template_sets_app, ["show", "ghost"])
    assert result.exit_code == 1
    assert "Template-set 'ghost' not found" in result.stdout


@pytest.mark.unit
def test_templates_add_installs(monkeypatch, tmp_path):
    called = {}

    def fake_run_handler(args):
        called.update(args)
        return {"installed": ["demo"]}

    monkeypatch.setattr("peagen.cli.commands.templates._run_handler", fake_run_handler)
    runner = CliRunner()
    result = runner.invoke(local_template_sets_app, ["add", "demo-src"])
    assert result.exit_code == 0
    assert "Installed template-set" in result.stdout
    assert called["source"] == "demo-src"
    assert not called["force"]


@pytest.mark.unit
def test_templates_add_prevents_overwrite(monkeypatch):
    def fake_run_handler(args):
        return {"installed": []}

    monkeypatch.setattr("peagen.cli.commands.templates._run_handler", fake_run_handler)
    runner = CliRunner()
    result = runner.invoke(local_template_sets_app, ["add", "demo-src"])
    assert result.exit_code == 0
    assert "no *new* template-set entry-point" in result.stdout
