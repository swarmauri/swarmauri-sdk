import inspect

import pytest

from tigrbl import TigrblApp
from tigrbl.orm.tables import Base
from tigrbl.orm.mixins import (
    GUIDPk,
    BulkCapable,
    Replaceable,
    Mergeable,
)
from tigrbl.types import Column, String


def _rpc_param_names(fn):
    return list(inspect.signature(fn).parameters.keys())


def _rest_aliases(model):
    return {route.name.split(".", 1)[1] for route in model.rest.router.routes}


def _rest_param_names(route):
    return set(inspect.signature(route.endpoint).parameters.keys())


def _assert_symmetry(model, verbs, rest_params):
    api = TigrblApp()
    api.include_model(model, mount_router=False)

    expected_verbs = set(verbs)
    rpc_aliases = set(getattr(model.rpc, "__dict__", {}).keys())
    assert rpc_aliases == expected_verbs

    rest_aliases = _rest_aliases(model)
    assert rest_aliases == expected_verbs

    for alias in expected_verbs:
        params = _rpc_param_names(getattr(model.rpc, alias))
        assert params == ["payload", "db", "request", "ctx"]

    for route in model.rest.router.routes:
        alias = route.name.split(".", 1)[1]
        params = _rest_param_names(route)
        assert params == rest_params[alias]


@pytest.mark.xfail(reason="REST/RPC parity pending header support in JSON-RPC methods")
def test_rest_rpc_symmetry_for_default_verbs():
    Base.metadata.clear()

    class Thing(Base, GUIDPk):
        __tablename__ = "things"
        __tigrbl_defaults_mode__ = "none"
        name = Column(String, nullable=False)

    Thing.__tigrbl_ops__ = {
        verb: {"target": verb}
        for verb in [
            "create",
            "read",
            "update",
            "replace",
            "delete",
            "list",
            "clear",
        ]
    }

    _assert_symmetry(
        Thing,
        Thing.__tigrbl_ops__.keys(),
        {
            "create": {"request", "db", "body"},
            "read": {"item_id", "request", "db"},
            "update": {"item_id", "request", "db", "body"},
            "replace": {"item_id", "request", "db", "body"},
            "delete": {"item_id", "request", "db"},
            "list": {"request", "q", "db"},
            "clear": {"request", "db"},
        },
    )


@pytest.mark.xfail(reason="REST/RPC parity pending header support in JSON-RPC methods")
def test_rest_rpc_symmetry_for_bulk_verbs():
    Base.metadata.clear()

    class Thing(Base, GUIDPk, BulkCapable):
        __tablename__ = "things"
        __tigrbl_defaults_mode__ = "none"
        name = Column(String, nullable=False)

    Thing.__tigrbl_ops__ = {
        verb: {"target": verb} for verb in ["bulk_create", "bulk_update", "bulk_delete"]
    }

    _assert_symmetry(
        Thing,
        Thing.__tigrbl_ops__.keys(),
        {
            "bulk_create": {"request", "db", "body"},
            "bulk_update": {"request", "db", "body"},
            "bulk_delete": {"request", "db", "body"},
        },
    )


@pytest.mark.xfail(reason="REST/RPC parity pending header support in JSON-RPC methods")
def test_rest_rpc_symmetry_for_replaceable_verbs():
    Base.metadata.clear()

    class Thing(Base, GUIDPk, BulkCapable, Replaceable):
        __tablename__ = "things"
        __tigrbl_defaults_mode__ = "none"
        name = Column(String, nullable=False)

    Thing.__tigrbl_ops__ = {
        verb: {"target": verb} for verb in ["replace", "bulk_replace"]
    }

    _assert_symmetry(
        Thing,
        Thing.__tigrbl_ops__.keys(),
        {
            "replace": {"item_id", "request", "db", "body"},
            "bulk_replace": {"request", "db", "body"},
        },
    )


@pytest.mark.xfail(reason="REST/RPC parity pending header support in JSON-RPC methods")
def test_rest_rpc_symmetry_for_mergeable_verbs():
    Base.metadata.clear()

    class Thing(Base, GUIDPk, BulkCapable, Mergeable):
        __tablename__ = "things"
        __tigrbl_defaults_mode__ = "none"
        name = Column(String, nullable=False)

    Thing.__tigrbl_ops__ = {verb: {"target": verb} for verb in ["merge", "bulk_merge"]}

    _assert_symmetry(
        Thing,
        Thing.__tigrbl_ops__.keys(),
        {
            "merge": {"item_id", "request", "db", "body"},
            "bulk_merge": {"request", "db", "body"},
        },
    )
