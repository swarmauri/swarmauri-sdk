from __future__ import annotations

from pathlib import Path

PKG = Path(__file__).resolve().parents[3] / "tigrbl" / "tigrbl"


def test_dependency_invoke_is_runtime_event_anchor():
    events = (PKG / "runtime" / "events.py").read_text()
    assert "DEP_EXTRA" in events
    assert '"PRE_TX_BEGIN"' in events


def test_runtime_gateway_owns_runtime_entrypoint_and_send():
    invoke_source = (PKG / "runtime" / "gw" / "invoke.py").read_text()
    assert "kernel.kernel_plan(app)" in invoke_source
    assert "await _invoke(" in invoke_source
    assert "_send_transport_response" in invoke_source


def test_docs_generation_reads_secdeps_metadata():
    openapi = (PKG / "system" / "docs" / "openapi" / "schema.py").read_text()
    openrpc = (PKG / "system" / "docs" / "openrpc.py").read_text()
    assert "secdeps" in openapi
    assert 'item["name"]' in openrpc
