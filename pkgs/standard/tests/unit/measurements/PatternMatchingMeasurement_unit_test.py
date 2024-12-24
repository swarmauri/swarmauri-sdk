import pytest
from swarmauri.measurements.concrete.PatternMatchingMeasurement import (
    PatternMatchingMeasurement as Measurement,
)


@pytest.mark.unit
def test_ubc_resource():
    assert Measurement(value=10).resource == "Measurement"


@pytest.mark.unit
def test_ubc_type():
    measurement = Measurement(value=10)
    assert measurement.type == "PatternMatchingMeasurement"


@pytest.mark.unit
def test_serialization():
    measurement = Measurement(value=10)
    assert measurement.id == Measurement.model_validate_json(measurement.model_dump_json()).id


@pytest.mark.unit
def test_measurement_value():
    assert Measurement(value=10)() == 10


@pytest.mark.unit
def test_measurement_unit():
    assert Measurement(value=10).unit == "percentage"
