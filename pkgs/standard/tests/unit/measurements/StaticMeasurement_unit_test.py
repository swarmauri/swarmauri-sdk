import pytest
from swarmauri.measurements.concrete.StaticMeasurement import StaticMeasurement as Measurement

@pytest.mark.unit
def test_ubc_resource():
    def test():
        assert Measurement(unit='jar of honey', value=10).resource == 'Measurement'
    test()

@pytest.mark.unit
def test_ubc_type():
    measurement = Measurement(unit='points', value=10)
    assert measurement.type == 'StaticMeasurement'

@pytest.mark.unit
def test_serialization():
    measurement = Measurement(unit='points', value=10)
    assert measurement.id == Measurement.model_validate_json(measurement.model_dump_json()).id


@pytest.mark.unit
def test_measurement_value():
	def test():
		assert Measurement(unit='jar of honey', value=10)() == 10
		assert Measurement(unit='jar of honey', value=10).value == 10
	test()


@pytest.mark.unit
def test_measurement_unit():
	def test():
		assert Measurement(unit='jar of honey', value=10).unit == 'jar of honey'
	test()