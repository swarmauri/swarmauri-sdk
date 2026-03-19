from __future__ import annotations

from pathlib import Path

_STANDARDS = Path(__file__).resolve().parents[3]
PKG = _STANDARDS / "tigrbl" / "tigrbl"
RUNTIME_PKG = _STANDARDS / "tigrbl_runtime" / "tigrbl_runtime"


def test_dependency_invoke_is_runtime_event_anchor():
    events = (RUNTIME_PKG / "runtime" / "events.py").read_text()
    assert "DEP_EXTRA" in events
    assert '"PRE_TX_BEGIN"' in events


def test_runtime_gateway_owns_runtime_entrypoint_and_send():
    runtime_source = (RUNTIME_PKG / "runtime" / "runtime.py").read_text()
    executor_source = (RUNTIME_PKG / "executors" / "kernel_executor.py").read_text()
    packed_source = (RUNTIME_PKG / "executors" / "packed.py").read_text()

    assert "kernel.kernel_plan(app)" in runtime_source
    assert "await _invoke(" in executor_source
    assert "_send_transport_response" in packed_source


def test_docs_generation_reads_secdeps_metadata():
    openapi = (PKG / "system" / "docs" / "openapi" / "schema.py").read_text()
    openrpc = (PKG / "system" / "docs" / "openrpc.py").read_text()
    assert "secdeps" in openapi
    assert 'item["name"]' in openrpc
