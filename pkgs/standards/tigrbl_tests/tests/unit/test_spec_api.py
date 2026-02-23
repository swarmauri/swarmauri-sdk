from tigrbl.api.mro_collect import mro_collect_api_hooks
from tigrbl.api.shortcuts import defineApiSpec, deriveApi
from tigrbl.config.constants import TIGRBL_API_HOOKS_ATTR


def _sample_hook(ctx):
    return ctx


def _override_hook(ctx):
    return ctx


class BaseApiSpec(defineApiSpec(name="tenant", prefix="/t", tags=("base",))):
    pass


class ChildApi(BaseApiSpec):
    TAGS = ("child",)


def test_api_spec_shortcuts_and_defaults():
    Derived = deriveApi(name="svc", prefix="/svc", tags=("svc",))
    assert Derived.NAME == "svc"
    assert Derived.PREFIX == "/svc"
    assert Derived.TAGS == ("svc",)


def test_api_hook_mro_collection():
    class Base:
        pass

    setattr(
        Base,
        TIGRBL_API_HOOKS_ATTR,
        {"read": {"pre": [_sample_hook]}},
    )

    class Child(Base):
        pass

    setattr(
        Child,
        TIGRBL_API_HOOKS_ATTR,
        {"read": {"pre": [_override_hook]}, "list": {"post": [_sample_hook]}},
    )

    hooks = mro_collect_api_hooks(Child)
    assert hooks["read"]["pre"] == [_sample_hook, _override_hook]
    assert hooks["list"]["post"] == [_sample_hook]
