import importlib

import pytest


def test_base_is_exported() -> None:
    module = importlib.import_module("tigrbl.orm.tables")
    assert hasattr(module, "Base")


def test_base_is_singleton() -> None:
    from tigrbl.orm.tables import Base as table_base
    from tigrbl.orm.tables import Base as orm_base

    assert table_base is orm_base


@pytest.mark.parametrize("invalid_path", ["tigrbl.orm.table"])
def test_invalid_import_path_raises(invalid_path: str) -> None:
    with pytest.raises(ModuleNotFoundError):
        importlib.import_module(invalid_path)
