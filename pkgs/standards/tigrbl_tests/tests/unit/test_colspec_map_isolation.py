from tigrbl import TableBase
from tigrbl.column import makeVirtualColumn


class Base:
    base = makeVirtualColumn()


class One(TableBase):
    one = makeVirtualColumn()


class Two(TableBase):
    two = makeVirtualColumn()


def test_colspec_maps_are_isolated() -> None:
    assert set(Base.__tigrbl_colspecs__) == {"base"}
    assert set(One.__tigrbl_colspecs__) == {"base", "one"}
    assert set(Two.__tigrbl_colspecs__) == {"base", "two"}
