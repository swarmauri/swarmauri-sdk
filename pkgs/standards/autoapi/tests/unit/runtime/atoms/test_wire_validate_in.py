from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from autoapi.v3.runtime.atoms.wire import validate_in


def test_validate_in_missing_required() -> None:
    schema_in = {"by_field": {}, "required": ("name",)}
    ctx = SimpleNamespace(temp={"schema_in": schema_in, "in_values": {}}, specs={})
    with pytest.raises(HTTPException):
        validate_in.run(None, ctx)
    assert ctx.temp["in_invalid"] is True


class Field:
    py_type = int


class Col:
    field = Field()


def test_validate_in_coerces_types() -> None:
    schema_in = {"by_field": {"age": {}}, "required": ()}
    ctx = SimpleNamespace(
        temp={"schema_in": schema_in, "in_values": {"age": "5"}}, specs={"age": Col()}
    )
    validate_in.run(None, ctx)
    assert ctx.temp["in_values"]["age"] == 5
    assert ctx.temp["in_coerced"] == ("age",)
