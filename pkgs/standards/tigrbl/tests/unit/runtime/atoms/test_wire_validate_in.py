from types import SimpleNamespace

import pytest

from tigrbl.runtime.atoms.wire import validate_in
from tigrbl.runtime.errors import HTTPException
from tigrbl.runtime.kernel import (
    SchemaIn,
    SchemaOut,
    OpView,
    _default_kernel as K,
)


def test_validate_in_missing_required() -> None:
    class App:
        pass

    app = App()

    class Model:
        pass

    alias = "create"
    ov = OpView(
        schema_in=SchemaIn(fields=("name",), by_field={"name": {"required": True}}),
        schema_out=SchemaOut(fields=(), by_field={}, expose=()),
        paired_index={},
        virtual_producers={},
        to_stored_transforms={},
        refresh_hints=(),
    )
    K._opviews[app] = {(Model, alias): ov}
    K._primed[app] = True

    ctx = SimpleNamespace(app=app, model=Model, op=alias, temp={"in_values": {}})
    with pytest.raises(HTTPException) as exc:
        validate_in.run(None, ctx)
    assert exc.value.status_code == 422
    assert ctx.temp["in_invalid"] is True


def test_validate_in_coerces_types() -> None:
    class App:
        pass

    app = App()

    class Model:
        pass

    alias = "create"
    ov = OpView(
        schema_in=SchemaIn(fields=("age",), by_field={"age": {"py_type": int}}),
        schema_out=SchemaOut(fields=(), by_field={}, expose=()),
        paired_index={},
        virtual_producers={},
        to_stored_transforms={},
        refresh_hints=(),
    )
    K._opviews[app] = {(Model, alias): ov}
    K._primed[app] = True

    ctx = SimpleNamespace(
        app=app, model=Model, op=alias, temp={"in_values": {"age": "5"}}
    )
    validate_in.run(None, ctx)
    assert ctx.temp["in_values"]["age"] == 5
    assert ctx.temp["in_coerced"] == ("age",)
