from __future__ import annotations

import importlib


def test_tigrbl_orm_alias_module_loads() -> None:
    orm = importlib.import_module("tigrbl.orm")
    assert orm.__name__ == "tigrbl.orm"


def test_tigrbl_orm_mixins_module_alias_loads() -> None:
    mixins = importlib.import_module("tigrbl.orm.mixins")
    assert mixins is not None


def test_bootstrappable_available_through_tigrbl_orm_mixins() -> None:
    from tigrbl.orm.mixins import Bootstrappable

    assert Bootstrappable.__name__ == "Bootstrappable"
