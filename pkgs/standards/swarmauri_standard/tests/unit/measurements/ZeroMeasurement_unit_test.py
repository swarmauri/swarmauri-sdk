import pytest
from swarmauri.measurements.concrete.ZeroMeasurement import ZeroMeasurement as Measurement

@pytest.mark.unit
def test_ubc_resource():
    assert Measurement().resource == 'Measurement'

@pytest.mark.unit
def test_ubc_type():
    measurement = Measurement()
    assert measurement.type == 'ZeroMeasurement'

@pytest.mark.unit
def test_serialization():
    measurement = Measurement()
    assert measurement.id == Measurement.model_validate_json(measurement.model_dump_json()).id


@pytest.mark.unit
def test_measurement_value():
    assert Measurement()() == 0
    assert Measurement().value == 0

@pytest.mark.unit
def test_measurement_unit():
    assert Measurement().unit == 'unitless'