from __future__ import annotations

import pytest

from tigrbl.bindings.model import bind
from tigrbl.bindings.schemas.defaults import _default_schemas_for_spec
from tigrbl.op import OpSpec
from tigrbl.orm.mixins import GUIDPk, KeyDigest
from tigrbl.orm.tables import Base
from tigrbl.schema import _build_schema
from tigrbl.specs import IO, S, acol
from tigrbl.types import String


class RouterKeyModel(Base, GUIDPk, KeyDigest):
    __tablename__ = "apikey_schema_selection"
    __resource__ = "apikey"
    __allow_unmapped__ = True

    label = acol(
        storage=S(String, nullable=False),
        io=IO(in_verbs=("create",), out_verbs=("read", "list", "create")),
    )


@pytest.mark.parametrize(
    ("target", "expected_out_item", "expect_deleted_out"),
    [
        ("create", None, False),
        ("read", None, False),
        ("update", None, False),
        ("replace", None, False),
        ("merge", None, False),
        ("delete", None, False),
        ("list", None, False),
        ("clear", None, True),
        ("bulk_create", "read", False),
        ("bulk_update", "read", False),
        ("bulk_replace", "read", False),
        ("bulk_merge", "read", False),
        ("bulk_delete", None, True),
    ],
)
def test_default_schema_selection_for_all_canonical_targets(
    target: str,
    expected_out_item: str | None,
    expect_deleted_out: bool,
):
    spec = OpSpec(alias=target, target=target)

    defaults = _default_schemas_for_spec(RouterKeyModel, spec)

    assert defaults["in_"] is not None
    assert defaults["out"] is not None

    if target in {"bulk_create", "bulk_update", "bulk_replace", "bulk_merge"}:
        assert defaults["in_item"] is not None
        assert defaults["out_item"] is not None
    else:
        assert defaults["in_item"] is None
        assert defaults["out_item"] is None

    if expect_deleted_out:
        assert "deleted" in defaults["out"].model_fields
    elif expected_out_item == "read":
        assert defaults["out_item"] is _build_schema(RouterKeyModel, verb="read")


def test_default_create_out_schema_matches_read_schema():
    spec = OpSpec(alias="create", target="create")

    defaults = _default_schemas_for_spec(RouterKeyModel, spec)
    read_schema = _build_schema(RouterKeyModel, verb="read")

    assert defaults["out"] is read_schema


def test_default_create_out_schema_excludes_create_only_alias_fields():
    spec = OpSpec(alias="create", target="create")

    defaults = _default_schemas_for_spec(RouterKeyModel, spec)

    assert defaults["out"] is not None
    assert "digest" in defaults["out"].model_fields
    assert "api_key" not in defaults["out"].model_fields


def test_default_custom_target_uses_alias_specific_io_sets():
    class CustomModel(Base, GUIDPk):
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

    bind(CustomModel)

    spec = OpSpec(alias="tokenize", target="custom")
    defaults = _default_schemas_for_spec(CustomModel, spec)

    assert defaults["in_"] is not None
    assert defaults["out"] is not None
    assert set(defaults["in_"].model_fields) == {"incoming"}
    assert set(defaults["out"].model_fields) == {"outgoing"}
