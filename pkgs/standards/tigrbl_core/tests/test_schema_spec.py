from __future__ import annotations

import sys
import types


def _install_schema_types_stub() -> None:
    module = types.ModuleType("tigrbl_core.schema.types")
    module.SchemaArg = object
    module.SchemaKind = str
    module.SchemaRef = dict
    sys.modules[module.__name__] = module


def test_schema_spec_fields() -> None:
    _install_schema_types_stub()

    from tigrbl_core._spec.schema_spec import SchemaSpec

    spec = SchemaSpec(alias="public", kind="out", schema={"name": "Demo"})

    assert spec.alias == "public"
    assert spec.kind == "out"
    assert spec.schema == {"name": "Demo"}
