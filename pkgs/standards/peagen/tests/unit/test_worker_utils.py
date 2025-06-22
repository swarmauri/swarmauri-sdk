import socket
import pytest
from peagen.worker.base import get_local_ip


@pytest.mark.unit
def test_get_local_ip_handles_error(monkeypatch):
    def fake_connect(self, addr):
        raise OSError()

    monkeypatch.setattr(socket.socket, "connect", fake_connect)
    assert get_local_ip() == "127.0.0.1"
