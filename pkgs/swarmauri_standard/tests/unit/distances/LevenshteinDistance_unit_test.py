import pytest
from swarmauri_standard.distances.LevenshteinDistance import (
    LevenshteinDistance,
)
from swarmauri_standard.vectors.Vector import Vector


@pytest.mark.unit
def test_compatibility_serialization():
    distance = LevenshteinDistance()
    assert (
        distance.id
        == LevenshteinDistance.model_validate_json(
            distance.model_dump_json()
        ).id
    )


@pytest.mark.unit
def test_compatibility_distance():
    assert (
        LevenshteinDistance().distance(
            Vector(value=[1, 2]), Vector(value=[1, 2])
        )
        == 0.0
    )
