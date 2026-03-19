import pytest

from tigrbl_base._base._table_registry_base import TableRegistryBase


class Model:
    __name__ = "Model"


class SAStyleModel:
    __name__ = "SAStyleModel"
    __table__ = "table-object"


def test_table_registry_base_register_and_lookup() -> None:
    registry = TableRegistryBase([Model])

    assert registry["Model"] is Model
    registry.register(("alias", SAStyleModel))
    assert registry["alias"] is SAStyleModel
    assert registry["SAStyleModel"] is SAStyleModel
    assert registry.SAStyleModel == "table-object"


def test_table_registry_base_setattr_and_missing_attr() -> None:
    registry = TableRegistryBase()
    registry.dynamic = Model
    assert registry["dynamic"] is Model

    with pytest.raises(AttributeError):
        _ = registry.missing
