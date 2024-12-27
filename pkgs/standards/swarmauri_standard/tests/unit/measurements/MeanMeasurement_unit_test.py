import pytest
from swarmauri.measurements.concrete.MeanMeasurement import MeanMeasurement as Measurement

@pytest.mark.unit
def test_ubc_resource():
	assert Measurement(unit='average test score').resource == 'Measurement'

@pytest.mark.unit
def test_ubc_type():
    measurement = Measurement(unit='average test score')
    assert measurement.type == 'MeanMeasurement'

@pytest.mark.unit
def test_serialization():
    measurement = Measurement(unit='points', value=10)
    assert measurement.id == Measurement.model_validate_json(measurement.model_dump_json()).id

@pytest.mark.unit
def test_measurement_value():
	measurement = Measurement(unit='average test score')
	measurement.add_measurement(10)
	measurement.add_measurement(100)

	assert measurement() == 55.0
	assert measurement.value == 55.0

@pytest.mark.unit
def test_measurement_unit():
	measurement = Measurement(unit='average test score')
	measurement.add_measurement(10)
	measurement.add_measurement(100)
	assert measurement.unit == 'average test score'