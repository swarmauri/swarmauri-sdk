from typer.testing import CliRunner
from peagen.commands.queue import queue_app
from peagen.queue.stub_queue import StubQueue
from peagen.queue.model import Task, TaskKind


def test_queue_list_shows_tasks(monkeypatch):
    q = StubQueue()
    q.enqueue(Task(TaskKind.RENDER, "t1", {}, set()))
    q.enqueue(Task(TaskKind.MUTATE, "t2", {}, set()))

    monkeypatch.setattr("peagen.commands.queue.make_queue", lambda *a, **k: q)
    runner = CliRunner()
    result = runner.invoke(queue_app, ["list", "--limit", "2"])
    assert result.exit_code == 0
    assert "t1" in result.output
    assert "t2" in result.output


def test_queue_list_with_offset(monkeypatch):
    q = StubQueue()
    q.enqueue(Task(TaskKind.RENDER, "t1", {}, set()))
    q.enqueue(Task(TaskKind.MUTATE, "t2", {}, set()))

    monkeypatch.setattr("peagen.commands.queue.make_queue", lambda *a, **k: q)
    runner = CliRunner()
    result = runner.invoke(queue_app, ["list", "--limit", "1", "--offset", "1"])
    assert result.exit_code == 0
    assert "t1" not in result.output
    assert "t2" in result.output
