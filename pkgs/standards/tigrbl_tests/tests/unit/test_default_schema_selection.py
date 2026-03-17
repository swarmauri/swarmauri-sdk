from __future__ import annotations

import pytest

from tigrbl import bind
from tigrbl._spec import OpSpec
from tigrbl.orm.mixins import GUIDPk, KeyDigest
from tigrbl.orm.tables import TableBase
from tigrbl.schema import _build_schema
from tigrbl._spec import IO, S
from tigrbl.shortcuts.column import acol
from tigrbl.types import String


def _default_schemas_for_spec(model: type, spec: OpSpec) -> dict[str, object | None]:
    bind(model)
    alias_ns = getattr(getattr(model, "schemas", object()), spec.alias, None)
    return {
        "in_": getattr(alias_ns, "in_", None),
        "out": getattr(alias_ns, "out", None),
        "in_item": None,
        "out_item": None,
    }


def _build_router_key_model() -> type:
    class RouterKeyModel(TableBase, GUIDPk, KeyDigest):
        __tablename__ = "apikey_schema_selection"
        __resource__ = "apikey"
        __allow_unmapped__ = True

        label = acol(
            storage=S(String, nullable=False),
            io=IO(in_verbs=("create",), out_verbs=("read", "list", "create")),
        )

    return RouterKeyModel


@pytest.mark.parametrize(
    ("target", "expect_bound"),
    [
        ("create", True),
        ("read", True),
        ("update", True),
        ("replace", True),
        ("merge", False),
        ("delete", True),
        ("list", True),
        ("clear", True),
        ("bulk_create", False),
        ("bulk_update", False),
        ("bulk_replace", False),
        ("bulk_merge", False),
        ("bulk_delete", False),
    ],
)
def test_default_schema_selection_for_all_canonical_targets(
    target: str,
    expect_bound: bool,
):
    model = _build_router_key_model()
    spec = OpSpec(alias=target, target=target)

    defaults = _default_schemas_for_spec(model, spec)

    if expect_bound:
        assert defaults["in_"] is not None
        assert defaults["out"] is not None
    else:
        assert defaults["in_"] is None
        assert defaults["out"] is None

    assert defaults["in_item"] is None
    assert defaults["out_item"] is None


def test_default_create_out_schema_matches_read_schema():
    model = _build_router_key_model()
    spec = OpSpec(alias="create", target="create")

    defaults = _default_schemas_for_spec(model, spec)
    read_schema = _build_schema(model, verb="read")

    assert defaults["out"] is not read_schema


def test_default_create_out_schema_excludes_create_only_alias_fields():
    model = _build_router_key_model()
    spec = OpSpec(alias="create", target="create")

    defaults = _default_schemas_for_spec(model, spec)

    assert defaults["out"] is not None
    assert "digest" in defaults["out"].model_fields
    assert "api_key" not in defaults["out"].model_fields


def test_default_custom_target_uses_alias_specific_io_sets():
    class CustomModel(TableBase, GUIDPk):
        __tablename__ = "custom_schema_selection"
        __resource__ = "custom"
        __allow_unmapped__ = True

        incoming = acol(
            storage=S(String, nullable=False),
            io=IO(in_verbs=("tokenize",), out_verbs=()),
        )
        outgoing = acol(
            storage=S(String, nullable=False),
            io=IO(in_verbs=(), out_verbs=("tokenize",)),
        )

    spec = OpSpec(alias="tokenize", target="custom")
    defaults = _default_schemas_for_spec(CustomModel, spec)

    assert defaults["in_"] is None
    assert defaults["out"] is None
