import importlib
import socket
import threading
import time

import requests
import uvicorn


def test_uvicorn_startup(tmp_path, monkeypatch):
    db_path = tmp_path / "authn.db"
    monkeypatch.setenv("PG_DSN", f"sqlite+aiosqlite:///{db_path}")
    mod = importlib.reload(importlib.import_module("auto_authn.app"))

    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()

    config = uvicorn.Config(mod.app, host="127.0.0.1", port=port, log_level="error")
    server = uvicorn.Server(config)

    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    for _ in range(50):
        if server.started:
            break
        time.sleep(0.1)

    try:
        assert server.started
        resp = requests.get(f"http://127.0.0.1:{port}/docs")
        assert resp.status_code == 200
    finally:
        server.should_exit = True
        thread.join()
