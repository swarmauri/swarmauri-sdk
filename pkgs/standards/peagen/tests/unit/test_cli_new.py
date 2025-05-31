import pytest
from typer.testing import CliRunner
from peagen.cli import app
from peagen.spawner import SpawnerConfig
from peagen.worker import WorkerConfig


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
    assert "worker" in result.output


@pytest.mark.unit
def test_evolve_step_invokes_run(monkeypatch):
    runner = CliRunner()
    called = {}

    def fake(tf, ef, sel, mut, be, sync):
        called["args"] = (tf, ef, sel, mut, be, sync)

    monkeypatch.setattr("peagen.commands.evolve.evolve_step", fake)
    result = runner.invoke(
        app,
        [
            "evolve",
            "step",
            "--target-file",
            "foo.py",
            "--entry-fn",
            "bar",
            "--selector",
            "greedy",
            "--mutator",
            "simple",
            "--backend",
            "cpu",
            "--sync",
        ],
    )
    assert result.exit_code == 0
    assert called["args"] == ("foo.py", "bar", "greedy", "simple", "cpu", True)


@pytest.mark.unit
def test_evolve_run_invokes_run(monkeypatch):
    runner = CliRunner()
    called = {}

    def fake(gen, target_ms, checkpoint, resume, dash):
        called["args"] = (gen, target_ms, checkpoint, resume, dash)

    monkeypatch.setattr("peagen.commands.evolve.evolve_run", fake)
    result = runner.invoke(
        app,
        ["evolve", "run", "--generations", "200", "--dashboard"],
    )
    assert result.exit_code == 0
    assert called["args"] == (
        200,
        None,
        ".peagen/evo_checkpoint.msgpack",
        False,
        True,
    )


@pytest.mark.unit
def test_worker_start_invokes_correct_runner(monkeypatch):
    runner = CliRunner()
    called = {}

    class DummySpawner:
        def __init__(self, cfg):
            called["spawner_cfg"] = cfg

        def run(self):
            called["spawner_run"] = True

    class DummyWorker:
        def __init__(self, cfg):
            called["worker_cfg"] = cfg

        def run(self):
            called["worker_run"] = True

    monkeypatch.setattr("peagen.commands.worker.WarmSpawner", DummySpawner)
    monkeypatch.setattr("peagen.commands.worker.OneShotWorker", DummyWorker)
    monkeypatch.setattr(
        "peagen.commands.worker.SpawnerConfig.from_toml",
        lambda p: SpawnerConfig(queue_url="stub://", caps=[]),
    )
    monkeypatch.setattr(
        "peagen.commands.worker.WorkerConfig.from_env",
        lambda: WorkerConfig(queue_url="stub://", caps=set()),
    )

    # spawner path
    res = runner.invoke(app, ["worker", "start", "--warm-pool", "1", "--caps", "cpu"])
    assert res.exit_code == 0
    assert called.get("spawner_run")
    assert not called.get("worker_run")
    called.clear()

    # worker path
    res = runner.invoke(app, ["worker", "start", "--caps", "cpu", "--concurrency", "2"])
    assert res.exit_code == 0
    assert called.get("worker_run")

