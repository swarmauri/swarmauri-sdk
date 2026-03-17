from itertools import product
from types import SimpleNamespace

import pytest

from tigrbl import op_ctx
from tigrbl_concrete._mapping.model import _bind_model_hooks, _materialize_handlers
from tigrbl_core._spec.op_spec import _mro_collect_decorated_ops
from tigrbl.types import BaseModel


class TokenInventorySchema(BaseModel):
    access_tokens: int
    refresh_tokens: int


PERSIST_VARIANTS = (
    "default",
    "write",
    "append",
    "prepend",
    "override",
    "skip",
    "none",
    "read",
)
ARITY_VARIANTS = ("collection", "member")
RESPONSE_SCHEMA_VARIANTS = (None, TokenInventorySchema)


def _normalize_persist(persist: str) -> str:
    if persist in {"none", "read", "skip"}:
        return "skip"
    if persist in {"write", "default", "persist"}:
        return "default"
    return persist


def _build_custom_model(arity: str, response_schema, persist: str):
    class Model:
        __name__ = "Model"

        @op_ctx(
            alias="token_inventory",
            target="custom",
            arity=arity,
            response_schema=response_schema,
            persist=persist,
        )
        def token_inventory(
            cls, ctx
        ):  # pragma: no cover - runtime execution not needed
            return TokenInventorySchema(access_tokens=1, refresh_tokens=2)

    specs = tuple(_mro_collect_decorated_ops(Model))
    Model.opspecs = SimpleNamespace(all=tuple(specs))
    _materialize_handlers(Model, specs)
    _bind_model_hooks(Model, specs)
    return Model, specs[0]


@pytest.mark.parametrize(
    "arity,response_schema,persist",
    list(product(ARITY_VARIANTS, RESPONSE_SCHEMA_VARIANTS, PERSIST_VARIANTS)),
    ids=lambda v: getattr(v, "__name__", str(v)),
)
def test_op_ctx_custom_target_parameter_cross_product(
    arity: str, response_schema, persist: str
) -> None:
    model, spec = _build_custom_model(arity, response_schema, persist)

    assert spec.alias == "token_inventory"
    assert spec.target == "custom"
    assert spec.arity == arity
    assert spec.response_model is response_schema
    assert spec.persist == _normalize_persist(persist)

    # Custom-target handlers are wrapped by the default handler atom pipeline.
    handler_names = [fn.__name__ for fn in model.hooks.token_inventory.HANDLER]
    assert handler_names == ["_default_handler_step"]
