import pytest
from typer.testing import CliRunner
from peagen.cli import app


@pytest.mark.unit
def test_render_invokes_run(monkeypatch):
    runner = CliRunner()
    called = {}

    def fake(project, out, queue):
        called["args"] = (project, out, queue)

    monkeypatch.setattr("peagen.commands.render.run_render", fake)
    result = runner.invoke(app, ["render", "--project", "p.yaml", "--out", "dst", "--sync"])
    assert result.exit_code == 0
    assert called["args"] == ("p.yaml", "dst", False)


@pytest.mark.unit
def test_mutate_invokes_run(monkeypatch):
    runner = CliRunner()
    called = {}

    def fake(tf, ef, out, be, q):
        called["args"] = (tf, ef, out, be, q)

    monkeypatch.setattr("peagen.commands.mutate.run_mutate", fake)
    result = runner.invoke(app, [
        "mutate",
        "--target-file",
        "file.py",
        "--entry-fn",
        "func",
        "--backend",
        "llm",
        "--sync",
    ])
    assert result.exit_code == 0
    assert called["args"] == ("file.py", "func", "target_mutated.py", "llm", False)


@pytest.mark.unit
def test_help_lists_commands():
    runner = CliRunner()
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "render" in result.output
    assert "mutate" in result.output
    assert "evolve" in result.output

