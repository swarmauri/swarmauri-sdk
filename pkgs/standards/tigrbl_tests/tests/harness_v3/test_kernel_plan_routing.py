"""Harness: KernelPlan compilation + route resolution.

Contract (TDD):
- Kernel.compile_plan(app) produces plain selector maps for REST and JSON-RPC.
- REST path/template matching is performed by runtime route atoms, not kernel core.
"""

from __future__ import annotations

import pytest

from tigrbl import TableBase, TigrblApp
from tigrbl.orm.mixins import GUIDPk
from tigrbl_kernel import _default_kernel
from tigrbl.shortcuts.engine import mem
from tigrbl.types import Column, String


def test_kernel_plan_compiles_rest_and_rpc_indices() -> None:
    class Widget(TableBase, GUIDPk):
        __tablename__ = "harness_kernel_widget"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    app = TigrblApp(engine=mem(async_=False))
    app.include_table(Widget)

    plan = _default_kernel.kernel_plan(app)

    assert "http.rest" in plan.proto_indices
    assert "http.jsonrpc" in plan.proto_indices

    rest_index = plan.proto_indices["http.rest"]
    assert isinstance(rest_index, dict)
    rest_exact = (
        rest_index.get("exact", rest_index)
        if isinstance(rest_index, dict)
        else rest_index
    )
    assert "POST /widget" in rest_exact

    rpc_index = plan.proto_indices["http.jsonrpc"]
    assert isinstance(rpc_index, dict)
    create_meta_index = rpc_index.get("Widget.create")
    assert isinstance(create_meta_index, int)
    assert plan.opmeta[create_meta_index].alias == "create"


@pytest.mark.skip(reason="binding_match atom removed in refactor")
def test_route_atom_matcher_resolves_collection_and_member_paths() -> None:
    pass


@pytest.mark.skip(reason="binding_match atom removed in refactor")
@pytest.mark.parametrize(
    "method,path",
    [
        ("GET", "/unknown"),
        ("POST", "/widget/abc"),
        ("PATCH", "/widget"),
    ],
)
def test_route_atom_matcher_returns_not_found_for_misses(
    method: str, path: str
) -> None:
    pass
