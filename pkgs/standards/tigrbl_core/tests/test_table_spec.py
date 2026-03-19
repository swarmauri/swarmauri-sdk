from __future__ import annotations

from tigrbl_core._spec.table_spec import TableSpec


def test_post_init_promotes_model_ref_to_model() -> None:
    spec = TableSpec(model=None, model_ref="pkg.models:Widget")

    assert spec.model == "pkg.models:Widget"


def test_collect_and_init_subclass_use_normalization_helpers() -> None:
    class Demo(TableSpec):
        ENGINE = "sqlite://:memory:"
        OPS = ("list",)
        COLUMNS = ("id",)
        table_config = {}

    collected = TableSpec.collect(Demo)

    assert Demo.OPS == ("list",)
    assert Demo.COLUMNS == ("id",)
    assert Demo.table_config["engine"] == "sqlite://:memory:"
    assert collected.model is Demo
    assert collected.ops == ("list",)
