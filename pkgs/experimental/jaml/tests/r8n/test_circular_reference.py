import pytest
from jaml import round_trip_loads


@pytest.mark.unit
@pytest.mark.xfail(reason="Circular reference detection not fully implemented")
def test_circular_reference_basic():
    # Circular reference between a and b
    jml = """
[circular]
a = f"%{b}"
b = f"%{a}"
    """.strip()

    with pytest.raises(ValueError, match="Circular reference detected: a -> b -> a"):
        round_trip_loads(jml)


@pytest.mark.unit
@pytest.mark.xfail(reason="Nested circular reference detection not fully implemented")
def test_circular_reference_nested():
    # Circular reference involving nested tables
    jml = """
[config]
a = f"%{b}"
b = f"%{c}"

[config.nested]
c = f"%{a}"
    """.strip()

    with pytest.raises(
        ValueError,
        match="Circular reference detected: config.a -> config.b -> config.nested.c -> config.a",
    ):
        round_trip_loads(jml)


@pytest.mark.unit
@pytest.mark.xfail(reason="Indirect circular reference detection not fully implemented")
def test_indirect_circular_reference():
    # Indirect circular reference through multiple variables
    jml = """
[indirect]
x = f"%{y}"
y = f"%{z}"
z = f"%{x}"
    """.strip()

    with pytest.raises(
        ValueError, match="Circular reference detected: x -> y -> z -> x"
    ):
        round_trip_loads(jml)
