import pytest
from swamauri_metric_wasserstein.WassersteinMetric import WassersteinMetric
from swarmauri_standard.vectors.Vector import Vector


@pytest.mark.unit
def test_ubc_resource():
    assert WassersteinMetric().resource == "Metric"


@pytest.mark.unit
def test_ubc_type():
    assert WassersteinMetric().type == "WassersteinMetric"


@pytest.mark.unit
def test_serialization():
    distance = WassersteinMetric()
    assert (
        distance.id
        == WassersteinMetric.model_validate_json(distance.model_dump_json()).id
    )


@pytest.mark.unit
def test_distance_is_zero_for_identical_vectors():
    assert (
        WassersteinMetric().distance(Vector(value=[1, 2]), Vector(value=[1, 2])) == 0.0
    )


@pytest.mark.unit
def test_distance_for_shifted_vectors():
    assert (
        WassersteinMetric().distance(
            Vector(value=[0.0, 1.0, 2.0]),
            Vector(value=[1.0, 2.0, 3.0]),
        )
        == 1.0
    )


@pytest.mark.unit
def test_distance_rejects_empty_vectors():
    with pytest.raises(ValueError, match="non-empty vectors"):
        WassersteinMetric().distance(Vector(value=[]), Vector(value=[1.0]))


@pytest.mark.unit
def test_distance_rejects_nan_values():
    with pytest.raises(ValueError, match="does not accept NaN"):
        WassersteinMetric().distance(
            Vector(value=[1.0, float("nan")]), Vector(value=[1.0])
        )


@pytest.mark.unit
def test_distance_rejects_infinite_values():
    with pytest.raises(ValueError, match="finite values"):
        WassersteinMetric().distance(
            Vector(value=[1.0, float("inf")]), Vector(value=[1.0])
        )


@pytest.mark.unit
def test_distance_rejects_nan_values_in_second_vector():
    with pytest.raises(ValueError, match="does not accept NaN"):
        WassersteinMetric().distance(
            Vector(value=[1.0]), Vector(value=[1.0, float("nan")])
        )
