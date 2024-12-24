import pytest
import pandas as pd
from swarmauri.measurements.concrete.MissingnessMeasurement import (
    MissingnessMeasurement as Measurement,
)


@pytest.mark.unit
def test_ubc_resource():
    assert Measurement(unit="%").resource == "Measurement"


@pytest.mark.unit
def test_ubc_type():
    measurement = Measurement(unit="%")
    assert measurement.type == "MissingnessMeasurement"


@pytest.mark.unit
def test_serialization():
    measurement = Measurement(unit="%", value=25.0)
    assert (
        measurement.id
        == Measurement.model_validate_json(measurement.model_dump_json()).id
    )


@pytest.mark.unit
def test_measurement_value_with_dataframe():
    measurement = Measurement(unit="%")
    test_df = pd.DataFrame({"A": [1, None, 3, None], "B": [None, 2, None, 4]})
    assert measurement(test_df) == 50.0
    assert measurement.value == 50.0


@pytest.mark.unit
def test_measurement_value_with_list():
    measurement = Measurement(unit="%")
    test_list = [1, None, 3, None, 5]
    assert measurement(test_list) == 40.0
    assert measurement.value == 40.0


@pytest.mark.unit
def test_measurement_unit():
    measurement = Measurement(unit="%")
    assert measurement.unit == "%"


@pytest.mark.unit
def test_column_missingness():
    measurement = Measurement(unit="%")
    test_df = pd.DataFrame({"A": [1, None, 3, None], "B": [None, 2, None, 4]})
    column_scores = measurement.get_column_missingness(test_df)
    assert column_scores == {"A": 50.0, "B": 50.0}


@pytest.mark.unit
def test_empty_data():
    measurement = Measurement(unit="%")
    assert measurement([]) == 0.0
    assert measurement({}) == 0.0
    assert measurement(pd.DataFrame()) == 0.0


@pytest.mark.unit
def test_calculate_method():
    measurement = Measurement(unit="%")
    measurement.add_measurement(1.0)
    measurement.add_measurement(None)
    measurement.add_measurement(3.0)
    measurement.add_measurement(None)
    measurement.add_measurement(5.0)

    assert measurement.calculate() == 40.0
    assert measurement.value == 40.0


@pytest.mark.unit
def test_invalid_input():
    measurement = Measurement(unit="%")
    with pytest.raises(ValueError):
        measurement(42)  # Invalid input type


@pytest.mark.unit
def test_add_measurement():
    measurement = Measurement(unit="%")
    measurement.add_measurement(1.0)
    measurement.add_measurement(None)
    assert len(measurement.measurements) == 2
    assert measurement.measurements == [1.0, None]
