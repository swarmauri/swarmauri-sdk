import pytest
from swarmauri_community.measurements.concrete.TokenCountEstimatorMeasurement import (
    TokenCountEstimatorMeasurement as Measurement,
)


@pytest.mark.unit
def test_ubc_resource():
    def test():
        assert Measurement().resource == "Measurement"

    test()


@pytest.mark.unit
def test_ubc_type():
    measurement = Measurement()
    assert measurement.type == "TokenCountEstimatorMeasurement"


@pytest.mark.unit
def test_serialization():
    measurement = Measurement()
    assert (
        measurement.id
        == Measurement.model_validate_json(measurement.model_dump_json()).id
    )


@pytest.mark.unit
def test_measurement_value():
    def test():
        assert (
            Measurement().calculate(
                "Lorem ipsum odor amet, consectetuer adipiscing elit."
            )
            == 11
        )

    test()


@pytest.mark.unit
def test_measurement_unit():
    def test():
        assert Measurement().unit == "tokens"

    test()
