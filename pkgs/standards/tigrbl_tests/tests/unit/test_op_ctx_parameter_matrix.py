from itertools import product

import pytest

from tigrbl import op_ctx
from tigrbl.mapping.op_mro_collect import mro_collect_decorated_ops
from tigrbl.types import BaseModel


class StatusSchema(BaseModel):
    ok: bool


TARGET_VARIANTS = ("custom", "create", "read", "update", "delete", "list")
ARITY_VARIANTS = ("collection", "member")
RESPONSE_SCHEMA_VARIANTS = (None, StatusSchema)
PERSIST_VARIANTS = ("default", "append", "prepend", "override", "skip")


def _normalize_persist(persist: str) -> str:
    if persist in {"none", "read", "skip"}:
        return "skip"
    if persist in {"write", "default", "persist"}:
        return "default"
    return persist


@pytest.mark.parametrize(
    "target,arity,response_schema,persist",
    list(
        product(
            TARGET_VARIANTS,
            ARITY_VARIANTS,
            RESPONSE_SCHEMA_VARIANTS,
            PERSIST_VARIANTS,
        )
    ),
    ids=lambda v: getattr(v, "__name__", str(v)),
)
def test_op_ctx_parameter_matrix(target, arity, response_schema, persist):
    class MatrixModel:
        @op_ctx(
            alias="probe",
            target=target,
            arity=arity,
            response_schema=response_schema,
            persist=persist,
        )
        def probe(cls, ctx):  # pragma: no cover - declaration-only test
            return {"ok": True}

    spec = mro_collect_decorated_ops(MatrixModel)[0]

    assert spec.alias == "probe"
    assert spec.target == target
    assert spec.arity == arity
    assert spec.response_model is response_schema
    assert spec.persist == _normalize_persist(persist)


@pytest.mark.parametrize(
    "target, response_schema, persist",
    list(product(TARGET_VARIANTS, RESPONSE_SCHEMA_VARIANTS, PERSIST_VARIANTS)),
    ids=lambda v: getattr(v, "__name__", str(v)),
)
def test_op_ctx_parameter_matrix_infers_arity_when_omitted(
    target, response_schema, persist
):
    class MatrixModel:
        @op_ctx(
            alias="probe",
            target=target,
            response_schema=response_schema,
            persist=persist,
        )
        def probe(cls, ctx):  # pragma: no cover - declaration-only test
            return {"ok": True}

    spec = mro_collect_decorated_ops(MatrixModel)[0]

    expected_arity = (
        "collection" if target in {"custom", "create", "list"} else "member"
    )
    assert spec.alias == "probe"
    assert spec.target == target
    assert spec.arity == expected_arity
    assert spec.response_model is response_schema
    assert spec.persist == _normalize_persist(persist)
