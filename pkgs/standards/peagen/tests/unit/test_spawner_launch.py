import pytest

from peagen.spawner import WarmSpawner, SpawnerConfig


class DummyProc:
    def __init__(self, cmd, env=None):
        self.cmd = cmd
        self.env = env

    def poll(self):
        return None


@pytest.mark.unit
def test_launch_worker_adds_no_detach(monkeypatch):
    launched = {}
    def fake_popen(cmd, env=None):
        p = DummyProc(cmd, env)
        launched['proc'] = p
        return p
    monkeypatch.setattr('peagen.spawner.subprocess.Popen', fake_popen)

    cfg = SpawnerConfig(queue_url='stub://', caps=['cpu'])
    monkeypatch.setattr('peagen.spawner.make_queue', lambda *a, **k: None)
    sp = WarmSpawner(cfg)
    sp._launch_worker()

    assert '--no-detach' in launched['proc'].cmd
    assert sp.workers == [launched['proc']]
