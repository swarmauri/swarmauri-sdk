"""Harness: KernelPlan compilation + route resolution.

Contract (TDD):
- Kernel.compile_plan(app) produces a KernelPlan that can resolve:
  * REST collection routes (exact path)
  * REST member routes (templated path params like /widget/{item_id})
  * JSON-RPC methods (exact rpc_method)

This suite intentionally focuses on *plan artifacts* and a minimal matching
API, not on any particular routing framework.
"""

from __future__ import annotations

from typing import Any, Callable

import pytest

from tigrbl import Base, TigrblApp
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.runtime.kernel import _default_kernel
from tigrbl.types import Column, String


def _assert_has_match_api(rest_index: Any) -> Callable[[str, str], tuple[int, dict[str, str]]]:
    """Return a (method, path) -> (meta_index, path_params) matcher."""
    if callable(rest_index):
        return rest_index  # type: ignore[return-value]
    match = getattr(rest_index, "match", None)
    if callable(match):
        return match  # type: ignore[return-value]
    raise AssertionError(
        "KernelPlan.proto_indices['http.rest'] must be a matcher (callable or .match(method, path))"
    )


def test_kernel_plan_compiles_rest_and_rpc_indices() -> None:
    class Widget(Base, GUIDPk):
        __tablename__ = "harness_kernel_widget"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    app = TigrblApp(engine=mem(async_=False))
    app.include_table(Widget)

    plan = _default_kernel.kernel_plan(app)

    assert "http.rest" in plan.proto_indices
    assert "http.jsonrpc" in plan.proto_indices

    # JSON-RPC index must map method name -> opmeta index.
    rpc_index = plan.proto_indices["http.jsonrpc"]
    assert isinstance(rpc_index, dict)

    create_meta_index = rpc_index.get("Widget.create")
    assert isinstance(create_meta_index, int)
    assert plan.opmeta[create_meta_index].alias == "create"


def test_kernel_plan_rest_matcher_resolves_collection_and_member_paths() -> None:
    class Widget(Base, GUIDPk):
        __tablename__ = "harness_kernel_widget_match"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    app = TigrblApp(engine=mem(async_=False))
    app.include_table(Widget)

    plan = _default_kernel.kernel_plan(app)

    rest_match = _assert_has_match_api(plan.proto_indices["http.rest"])

    # Collection: POST /widget -> create
    meta_index, params = rest_match("POST", "/widget")
    assert plan.opmeta[meta_index].alias == "create"
    assert params == {}

    # Collection: GET /widget -> list
    meta_index, params = rest_match("GET", "/widget")
    assert plan.opmeta[meta_index].alias == "list"
    assert params == {}

    # Member: GET /widget/<id> -> read
    meta_index, params = rest_match("GET", "/widget/abc123")
    assert plan.opmeta[meta_index].alias == "read"
    assert params.get("item_id") == "abc123"

    # Member: PATCH /widget/<id> -> update
    meta_index, params = rest_match("PATCH", "/widget/abc123")
    assert plan.opmeta[meta_index].alias == "update"
    assert params.get("item_id") == "abc123"

    # Member: DELETE /widget/<id> -> delete
    meta_index, params = rest_match("DELETE", "/widget/abc123")
    assert plan.opmeta[meta_index].alias == "delete"
    assert params.get("item_id") == "abc123"


@pytest.mark.parametrize(
    "method,path",
    [
        ("GET", "/unknown"),
        ("POST", "/widget/abc"),  # collection verb on member
        ("PATCH", "/widget"),  # member verb on collection
    ],
)
def test_kernel_plan_rest_matcher_returns_not_found_for_misses(method: str, path: str) -> None:
    class Widget(Base, GUIDPk):
        __tablename__ = "harness_kernel_widget_misses"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    app = TigrblApp(engine=mem(async_=False))
    app.include_table(Widget)

    plan = _default_kernel.kernel_plan(app)
    rest_match = _assert_has_match_api(plan.proto_indices["http.rest"])

    with pytest.raises(KeyError):
        rest_match(method, path)
