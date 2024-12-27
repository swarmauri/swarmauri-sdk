import pytest
import pandas as pd
from swarmauri.measurements.concrete.UniquenessMeasurement import (
    UniquenessMeasurement as Measurement,
)


@pytest.mark.unit
def test_ubc_resource():
    assert Measurement(unit="%").resource == "Measurement"


@pytest.mark.unit
def test_ubc_type():
    measurement = Measurement(unit="%")
    assert measurement.type == "UniquenessMeasurement"


@pytest.mark.unit
def test_serialization():
    measurement = Measurement(unit="%", value=75.0)
    assert (
        measurement.id
        == Measurement.model_validate_json(measurement.model_dump_json()).id
    )


@pytest.mark.unit
def test_measurement_value():
    measurement = Measurement(unit="%")
    test_data = ["A", "B", "A", "C", "B", "D"]  # 4 unique values out of 6 total
    result = measurement.call(test_data)
    assert result == pytest.approx(
        66.66666666666667, rel=1e-9
    )  # Using approx for float comparison
    assert measurement.value == pytest.approx(66.66666666666667, rel=1e-9)


@pytest.mark.unit
def test_measurement_unit():
    measurement = Measurement(unit="%")
    test_data = ["A", "B", "A", "C"]
    measurement.call(test_data)
    assert measurement.unit == "%"


@pytest.mark.unit
def test_dataframe_uniqueness():
    measurement = Measurement(unit="%")
    df = pd.DataFrame({"col1": [1, 2, 2, 3], "col2": ["A", "A", "B", "C"]})
    result = measurement.call(df)
    assert result == pytest.approx(75.0)


@pytest.mark.unit
def test_column_uniqueness():
    measurement = Measurement(unit="%")
    df = pd.DataFrame({"col1": [1, 2, 2, 3], "col2": ["A", "A", "B", "C"]})
    column_uniqueness = measurement.get_column_uniqueness(df)
    assert column_uniqueness["col1"] == pytest.approx(75.0)
    assert column_uniqueness["col2"] == pytest.approx(75.0)


@pytest.mark.unit
def test_empty_input():
    measurement = Measurement(unit="%")
    assert measurement.call([]) == 0.0
    assert measurement.call({}) == 0.0
    assert measurement.call(pd.DataFrame()) == 0.0


@pytest.mark.unit
def test_dict_uniqueness():
    measurement = Measurement(unit="%")
    test_dict = {"a": 1, "b": 2, "c": 1, "d": 3}  # 3 unique values out of 4
    assert measurement.call(test_dict) == pytest.approx(75.0)


@pytest.mark.unit
def test_invalid_input():
    measurement = Measurement(unit="%")
    with pytest.raises(ValueError):
        measurement.call(42)  # Invalid input type
