import pytest
from swarmauri.vectors.concrete.Vector import Vector

@pytest.mark.unit
def test_ubc_resource():
    vector = Vector(value=[1, 2])
    assert vector.resource == 'Vector'

@pytest.mark.unit
def test_ubc_type():
    vector = Vector(value=[1, 2])
    assert vector.type == 'Vector'

@pytest.mark.unit
def test_serialization():
    vector = Vector(value=[1, 2])
    assert vector.id == Vector.model_validate_json(vector.model_dump_json()).id

@pytest.mark.unit
def test_value():
    vector = Vector(value=[1, 2])
    assert vector.value == [1, 2]

@pytest.mark.unit
def test_shape():
    vector = Vector(value=[1, 2])
    assert vector.shape == (2,)

# Additional tests for vector space axioms
@pytest.mark.unit
def test_closure_addition():
    v1 = Vector(value=[1, 2])
    v2 = Vector(value=[3, 4])
    result = v1 + v2
    assert isinstance(result, Vector)
    assert result.value == [4, 6]

@pytest.mark.unit
def test_closure_scalar_multiplication():
    v = Vector(value=[1, 2])
    scalar = 3
    result = scalar * v
    assert isinstance(result, Vector)
    assert result.value == [3, 6]

@pytest.mark.unit
def test_additive_identity():
    v = Vector(value=[1, 2])
    zero = v.zero
    result = v + zero
    assert result == v

@pytest.mark.unit
def test_additive_inverse():
    v = Vector(value=[1, 2])
    inverse = -v
    result = v + inverse
    assert result == v.zero

@pytest.mark.unit
def test_commutativity_addition():
    v1 = Vector(value=[1, 2])
    v2 = Vector(value=[3, 4])
    assert v1 + v2 == v2 + v1

@pytest.mark.unit
def test_distributivity_scalar_vector():
    v1 = Vector(value=[1, 2])
    v2 = Vector(value=[3, 4])
    scalar = 2
    result = scalar * (v1 + v2)
    assert result == scalar * v1 + scalar * v2

@pytest.mark.unit
def test_distributivity_scalar_scalar():
    v = Vector(value=[1, 2])
    scalar1 = 2
    scalar2 = 3
    result = (scalar1 + scalar2) * v
    assert result == scalar1 * v + scalar2 * v

@pytest.mark.unit
def test_compatibility_scalar_multiplication():
    v = Vector(value=[1, 2])
    scalar1 = 2
    scalar2 = 3
    result = (scalar1 * scalar2) * v
    assert result == scalar1 * (scalar2 * v)

@pytest.mark.unit
def test_scalar_multiplication_identity():
    v = Vector(value=[1, 2])
    result = 1 * v
    assert result == v

@pytest.mark.unit
def test_all_axioms():
    v1 = Vector(value=[1, 2])
    v2 = Vector(value=[3, 4])
    scalar1 = 2
    scalar2 = 3
    assert v1.check_all_axioms(v2, scalar1, scalar2)
