import importlib

import pytest


@pytest.mark.parametrize("module_path", ["autoapi.v3.table", "autoapi.v3.orm.tables"])
def test_base_is_exported(module_path: str) -> None:
    module = importlib.import_module(module_path)
    assert hasattr(module, "Base")


def test_base_is_singleton() -> None:
    from autoapi.v3.table import Base as table_base
    from autoapi.v3.orm.tables import Base as orm_base

    assert table_base is orm_base


@pytest.mark.parametrize(
    "invalid_path", ["autoapi.v3.table.base", "autoapi.v3.orm.table"]
)
def test_invalid_import_path_raises(invalid_path: str) -> None:
    with pytest.raises(ModuleNotFoundError):
        importlib.import_module(invalid_path)
