import pytest
from swarmauri_distance_wasserstein.WassersteinDistance import WassersteinDistance
from swarmauri_standard.vectors.Vector import Vector


@pytest.mark.unit
def test_ubc_resource():
    assert WassersteinDistance().resource == "Distance"


@pytest.mark.unit
def test_ubc_type():
    assert WassersteinDistance().type == "WassersteinDistance"


@pytest.mark.unit
def test_serialization():
    distance = WassersteinDistance()
    assert (
        distance.id
        == WassersteinDistance.model_validate_json(distance.model_dump_json()).id
    )


@pytest.mark.unit
def test_distance_is_zero_for_identical_vectors():
    assert (
        WassersteinDistance().distance(Vector(value=[1, 2]), Vector(value=[1, 2]))
        == 0.0
    )


@pytest.mark.unit
def test_distance_for_shifted_vectors():
    assert (
        WassersteinDistance().distance(
            Vector(value=[0.0, 1.0, 2.0]),
            Vector(value=[1.0, 2.0, 3.0]),
        )
        == 1.0
    )


@pytest.mark.unit
def test_distance_rejects_empty_vectors():
    with pytest.raises(ValueError, match="non-empty vectors"):
        WassersteinDistance().distance(Vector(value=[]), Vector(value=[1.0]))
