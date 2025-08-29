from autoapi.v3.specs import ColumnSpec


class Base:
    base = ColumnSpec(storage=None)


class One(Base):
    one = ColumnSpec(storage=None)


class Two(Base):
    two = ColumnSpec(storage=None)


def test_colspec_maps_are_isolated() -> None:
    assert set(Base.__autoapi_colspecs__) == {"base"}
    assert set(One.__autoapi_colspecs__) == {"base", "one"}
    assert set(Two.__autoapi_colspecs__) == {"base", "two"}
