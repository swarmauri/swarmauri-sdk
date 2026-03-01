from __future__ import annotations

from pathlib import Path

PKG = Path(__file__).resolve().parents[3] / "tigrbl" / "tigrbl"


def test_dependency_invoke_is_runtime_event_anchor():
    events = (PKG / "runtime" / "events.py").read_text()
    assert "DEP_EXTRA" in events
    assert '"PRE_TX_BEGIN"' in events


def test_runtime_gateway_owns_ingress_route_and_egress_send():
    executor = (PKG / "runtime" / "gw" / "executor.py").read_text()
    assert "_routing_atoms" in executor
    assert "kernel_plan(self.app)" in executor
    assert "_send_transport_response" in executor


def test_docs_generation_reads_secdeps_metadata():
    openapi = (PKG / "system" / "docs" / "openapi" / "schema.py").read_text()
    openrpc = (PKG / "system" / "docs" / "openrpc.py").read_text()
    assert "secdeps" in openapi
    assert 'item["name"]' in openrpc
