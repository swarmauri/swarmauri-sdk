import pytest
from swarmauri_standard.mutators.Mutator import Mutator


@pytest.mark.unit
def test_resource():
    assert Mutator().resource == "Mutator"


@pytest.mark.unit
def test_type():
    assert Mutator().type == "Mutator"


@pytest.mark.unit
def test_serialization():
    m = Mutator()
    assert m.id == Mutator.model_validate_json(m.model_dump_json()).id


@pytest.mark.unit
def test_mutate():
    m = Mutator()
    assert m.mutate(1) == 1
    assert m.mutates([1, 2]) == [1, 2]
