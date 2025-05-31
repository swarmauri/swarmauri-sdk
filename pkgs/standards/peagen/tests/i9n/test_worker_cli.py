from typer.testing import CliRunner
import json

from peagen.commands.worker import worker_app


class DummyProc:
    def __init__(self, pid, cmdline, env):
        self.pid = pid
        self._cmd = cmdline
        self._env = env

    def cmdline(self):
        return self._cmd


def _patch_process(monkeypatch, procs):
    proc_map = {p.pid: p for p in procs}
    monkeypatch.setattr(
        "peagen.commands.worker._find_workers",
        lambda: procs,
    )

    def fake_proc(pid):
        class P:
            def environ(self):
                return proc_map[pid]._env

        return P()

    monkeypatch.setattr("psutil.Process", fake_proc)


def test_list_workers_basic(monkeypatch):
    procs = [
        DummyProc(1, ["python", "-m", "peagen.cli", "worker", "start"], {}),
    ]
    _patch_process(monkeypatch, procs)

    runner = CliRunner()
    result = runner.invoke(worker_app, ["ps"])
    assert result.exit_code == 0
    lines = result.output.strip().splitlines()
    assert lines[0] == "PID\tCMD"
    assert lines[1].startswith("1\tpython -m peagen.cli worker start")


def test_list_workers_verbose(monkeypatch):
    procs = [
        DummyProc(
            2,
            ["python", "-m", "peagen.cli", "worker", "start"],
            {"QUEUE_URL": "q1", "WORKER_CAPS": "cpu", "WARM_POOL": "0"},
        ),
        DummyProc(
            3,
            ["python", "-m", "peagen.cli", "worker", "start"],
            {"QUEUE_URL": "q2", "WORKER_CAPS": "gpu", "WARM_POOL": "2"},
        ),
    ]
    _patch_process(monkeypatch, procs)

    runner = CliRunner()
    result = runner.invoke(worker_app, ["ps", "--verbose"])
    assert result.exit_code == 0
    lines = result.output.strip().splitlines()
    assert lines[0] == "PID\tQUEUE_URL\tWORKER_CAPS\tWARM_POOL\tCMD"
    assert "2\tq1\tcpu\t0\tpython -m peagen.cli worker start" in lines[1]
    assert "3\tq2\tgpu\t2\tpython -m peagen.cli worker start" in lines[2]


def test_worker_ps_json(monkeypatch):
    procs = [
        DummyProc(
            4,
            ["python", "-m", "peagen.cli", "worker", "start"],
            {
                "QUEUE_URL": "q1",
                "WORKER_CAPS": "cpu,docker",
                "WORKER_PLUGINS": "MutateHandler",
                "WORKER_CONCURRENCY": "1",
            },
        )
    ]
    _patch_process(monkeypatch, procs)

    runner = CliRunner()
    result = runner.invoke(worker_app, ["ps", "--json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data[0]["pid"] == 4
    assert data[0]["queue_url"] == "q1"
    assert data[0]["caps"] == ["cpu", "docker"]
    assert data[0]["plugins"] == ["MutateHandler"]
