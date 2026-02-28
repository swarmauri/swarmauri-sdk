from tigrbl import TableBase
from tigrbl.mapping.router_mro_collect import mro_collect_router_hooks
from tigrbl.shortcuts.router import defineRouterSpec, deriveRouter
from tigrbl.config.constants import TIGRBL_ROUTER_HOOKS_ATTR


def _sample_hook(ctx):
    return ctx


def _override_hook(ctx):
    return ctx


class BaseApiSpec(defineRouterSpec(name="tenant", prefix="/t", tags=("base",))):
    pass


class ChildApi(BaseApiSpec):
    TAGS = ("child",)


def test_router_spec_shortcuts_and_defaults():
    Derived = deriveRouter(name="svc", prefix="/svc", tags=("svc",))
    assert Derived.NAME == "svc"
    assert Derived.PREFIX == "/svc"
    assert Derived.TAGS == ("svc",)


def test_router_hook_mro_collection():
    class Base:
        pass

    setattr(
        TableBase,
        TIGRBL_ROUTER_HOOKS_ATTR,
        {"read": {"pre": [_sample_hook]}},
    )

    class Child(TableBase):
        pass

    setattr(
        Child,
        TIGRBL_ROUTER_HOOKS_ATTR,
        {"read": {"pre": [_override_hook]}, "list": {"post": [_sample_hook]}},
    )

    hooks = mro_collect_router_hooks(Child)
    assert hooks["read"]["pre"] == [_sample_hook, _override_hook]
    assert hooks["list"]["post"] == [_sample_hook]
