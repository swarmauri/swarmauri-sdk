import pytest
from swarmauri.measurements.concrete.FirstImpressionMeasurement import FirstImpressionMeasurement as Measurement

@pytest.mark.unit
def test_ubc_resource():
	assert Measurement(unit='points', value=10).resource == 'Measurement'


@pytest.mark.unit
def test_ubc_type():
    measurement = Measurement(unit='points', value=10)
    assert measurement.type == 'FirstImpressionMeasurement'

@pytest.mark.unit
def test_serialization():
    measurement = Measurement(unit='points', value=10)
    assert measurement.id == Measurement.model_validate_json(measurement.model_dump_json()).id

@pytest.mark.unit
def test_measurement_value():
	assert Measurement(unit='points', value=10)() == 10
	assert Measurement(unit='points', value=10).value == 10


@pytest.mark.unit
def test_measurement_unit():
	assert Measurement(unit='points', value=10).unit == 'points'