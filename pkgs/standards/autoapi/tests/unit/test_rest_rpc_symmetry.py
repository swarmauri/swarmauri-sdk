import inspect

from autoapi.v3 import AutoAPI
from autoapi.v3.tables import Base
from autoapi.v3.mixins import GUIDPk
from autoapi.v3.types import Column, String
from autoapi.v3.opspec.types import CANON


def _rpc_param_names(fn):
    return list(inspect.signature(fn).parameters.keys())


def _rest_aliases(model):
    return {route.name.split(".", 1)[1] for route in model.rest.router.routes}


def _rest_param_names(route):
    return set(inspect.signature(route.endpoint).parameters.keys())


def test_rest_rpc_symmetry_for_default_verbs():
    Base.metadata.clear()

    class Thing(Base, GUIDPk):
        __tablename__ = "things"
        name = Column(String, nullable=False)

    Thing.__autoapi_ops__ = {verb: {"target": verb} for verb in CANON}

    async def custom_handler(payload=None):
        return payload

    Thing.__autoapi_ops__["custom"]["handler"] = custom_handler

    api = AutoAPI()
    api.include_model(Thing, mount_router=False)

    expected_verbs = set(CANON)

    rpc_aliases = set(getattr(Thing.rpc, "__dict__", {}).keys())
    assert rpc_aliases == expected_verbs

    rest_aliases = _rest_aliases(Thing)
    assert rest_aliases == expected_verbs

    for alias in expected_verbs:
        params = _rpc_param_names(getattr(Thing.rpc, alias))
        assert params == ["payload", "db", "request", "ctx"]

    expected_rest_params = {
        "create": {"request", "db", "body"},
        "read": {"item_id", "request", "db"},
        "update": {"item_id", "request", "db", "body"},
        "replace": {"item_id", "request", "db", "body"},
        "delete": {"item_id", "request", "db"},
        "list": {"request", "q", "db"},
        "clear": {"request", "db"},
        "bulk_create": {"request", "db", "body"},
        "bulk_update": {"request", "db", "body"},
        "bulk_replace": {"request", "db", "body"},
        "bulk_delete": {"request", "db", "body"},
        "custom": {"request", "db", "body"},
    }

    for route in Thing.rest.router.routes:
        alias = route.name.split(".", 1)[1]
        params = _rest_param_names(route)
        assert params == expected_rest_params[alias]
