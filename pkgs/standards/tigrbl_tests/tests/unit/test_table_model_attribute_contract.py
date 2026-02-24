from __future__ import annotations

from sqlalchemy import Table

from tigrbl import TigrblApp, TigrblRouter


def test_table_objects_only_expose_model_attribute_contract():
    assert hasattr(Table, "_is_table")


def test_core_classes_do_not_expose_model_or_models_attributes():
    forbidden = ("model", "models")
    for cls in (TigrblApp, TigrblRouter):
        for attr in forbidden:
            assert not hasattr(cls, attr)
            assert not hasattr(cls(), attr)
