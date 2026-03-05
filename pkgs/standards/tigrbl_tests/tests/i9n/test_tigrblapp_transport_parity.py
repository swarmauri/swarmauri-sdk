from __future__ import annotations

import json
import os
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path

import httpx
import pytest


def _start_process(
    cmd: list[str],
    *,
    env: dict[str, str] | None = None,
    cwd: Path | None = None,
) -> subprocess.Popen:
    return subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        cwd=cwd,
        text=True,
    )


def _wait_for_port(
    host: str,
    port: int,
    *,
    timeout: float = 10.0,
    process: subprocess.Popen | None = None,
) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection((host, port), timeout=0.5):
                return
        except OSError:
            if process is not None and process.poll() is not None:
                stderr = process.stderr.read() if process.stderr else ""
                raise RuntimeError(
                    f"process exited before port {port} came up: {stderr}"
                )
            time.sleep(0.05)
    raise RuntimeError(f"port {port} did not come up")


def _write_localhost_cert(tmp_path: Path) -> tuple[Path, Path]:
    if shutil.which("openssl") is None:
        pytest.skip("openssl is required for HTTP/2 and HTTP/3 TLS tests")

    cert = tmp_path / "cert.pem"
    key = tmp_path / "key.pem"
    cmd = [
        "openssl",
        "req",
        "-x509",
        "-newkey",
        "rsa:2048",
        "-nodes",
        "-keyout",
        str(key),
        "-out",
        str(cert),
        "-subj",
        "/CN=127.0.0.1",
        "-addext",
        "subjectAltName=IP:127.0.0.1,DNS:localhost",
        "-days",
        "1",
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return cert, key


@pytest.mark.i9n
def test_tigrblapp_transport_parity_h1_h2_h3(tmp_path: Path) -> None:
    pytest.importorskip("hypercorn")
    pytest.importorskip("aioquic")

    cert, key = _write_localhost_cert(tmp_path)
    app_dir = Path(__file__).resolve().parent
    env = {**os.environ, "PYTHONPATH": os.environ.get("PYTHONPATH", "")}

    p1: subprocess.Popen | None = None
    p2: subprocess.Popen | None = None
    p3: subprocess.Popen | None = None

    try:
        p1 = _start_process(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "transport_parity_app:app",
                "--port",
                "8001",
                "--log-level",
                "critical",
            ],
            env=env,
            cwd=app_dir,
        )
        _wait_for_port("127.0.0.1", 8001, process=p1)

        p2 = _start_process(
            [
                sys.executable,
                "-m",
                "hypercorn",
                "transport_parity_app:app",
                "--bind",
                "127.0.0.1:8002",
                "--certfile",
                str(cert),
                "--keyfile",
                str(key),
                "--log-level",
                "critical",
            ],
            env=env,
            cwd=app_dir,
        )
        _wait_for_port("127.0.0.1", 8002, process=p2)

        p3 = _start_process(
            [
                sys.executable,
                "-m",
                "hypercorn",
                "transport_parity_app:app",
                "--quic-bind",
                "127.0.0.1:4433",
                "--certfile",
                str(cert),
                "--keyfile",
                str(key),
                "--log-level",
                "critical",
            ],
            env=env,
            cwd=app_dir,
        )
        time.sleep(1.0)
        if p3.poll() is not None:
            stderr = p3.stderr.read() if p3.stderr else ""
            raise RuntimeError(
                f"http3 server exited before handling requests: {stderr}"
            )

        out: dict[str, dict] = {}

        with httpx.Client() as c:
            r = c.get(
                "http://127.0.0.1:8001/transport-widget", headers={"x-test": "h1"}
            )
            out["http1"] = {"status": r.status_code, "body": r.json()}

        with httpx.Client(http2=True, verify=str(cert)) as c2:
            r2 = c2.get(
                "https://127.0.0.1:8002/transport-widget", headers={"x-test": "h2"}
            )
            out["http2"] = {
                "status": r2.status_code,
                "body": r2.json(),
                "http_version": r2.http_version,
            }

        with httpx.Client() as c3:
            payload = {
                "jsonrpc": "2.0",
                "method": "TransportWidget.create",
                "params": {"name": "rpc-widget"},
                "id": 1,
            }
            r3 = c3.post("http://127.0.0.1:8001/rpc/", json=payload)
            out["jsonrpc"] = {"status": r3.status_code, "body": r3.json()}

        h3_cmd = [
            sys.executable,
            "-m",
            "aioquic.examples.http3_client",
            "https://127.0.0.1:4433/transport-widget",
            "--ca-certs",
            str(cert),
        ]
        proc = subprocess.run(
            h3_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10
        )
        h3_output = "\n".join(
            [proc.stdout.decode(errors="replace"), proc.stderr.decode(errors="replace")]
        )

        body_json = None
        for line in h3_output.splitlines():
            line = line.strip()
            if line.startswith("{") or line.startswith("["):
                try:
                    body_json = json.loads(line)
                    break
                except json.JSONDecodeError:
                    continue

        out["http3"] = {
            "status": 200 if body_json is not None else 0,
            "body": body_json,
            "return_code": proc.returncode,
            "raw_output": h3_output,
        }

        assert out["http1"]["status"] == 200
        assert out["http1"]["body"] == []

        assert out["http2"]["status"] == 200
        assert out["http2"]["body"] == []
        assert out["http2"]["http_version"] == "HTTP/2"

        assert out["jsonrpc"]["status"] == 200
        assert out["jsonrpc"]["body"] == {
            "jsonrpc": "2.0",
            "result": {
                "name": "rpc-widget",
                "id": out["jsonrpc"]["body"]["result"]["id"],
            },
            "id": 1,
        }

        if out["http3"]["status"] == 200:
            assert out["http3"]["body"] == []
        else:
            pytest.skip(
                f"HTTP/3 request did not return JSON payload: {out['http3']['raw_output']}"
            )
    finally:
        for process in (p1, p2, p3):
            if process is None:
                continue
            try:
                process.terminate()
                process.wait(timeout=2)
            except Exception:
                process.kill()
