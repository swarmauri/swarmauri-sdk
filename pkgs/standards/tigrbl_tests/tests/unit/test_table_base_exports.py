import importlib

import pytest


@pytest.mark.parametrize("module_path", ["tigrbl", "tigrbl.orm.tables"])
def test_table_base_is_exported(module_path: str) -> None:
    module = importlib.import_module(module_path)
    assert hasattr(module, "TableBase")


def test_table_base_is_singleton() -> None:
    from tigrbl import TableBase
    from tigrbl.orm.tables import TableBase as orm_table_base

    assert TableBase is orm_table_base


@pytest.mark.parametrize("invalid_path", ["tigrbl.table", "tigrbl.table.base", "tigrbl.orm.table"])
def test_invalid_import_path_raises(invalid_path: str) -> None:
    with pytest.raises(ModuleNotFoundError):
        importlib.import_module(invalid_path)
