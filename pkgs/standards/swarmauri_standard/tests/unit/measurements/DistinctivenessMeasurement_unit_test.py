import pytest
import pandas as pd
from swarmauri.measurements.concrete.DistinctivenessMeasurement import (
    DistinctivenessMeasurement as Measurement,
)


@pytest.mark.unit
def test_ubc_resource():
    assert Measurement(unit="%").resource == "Measurement"


@pytest.mark.unit
def test_ubc_type():
    measurement = Measurement(unit="%")
    assert measurement.type == "DistinctivenessMeasurement"


@pytest.mark.unit
def test_serialization():
    measurement = Measurement(unit="%", value=75.0)
    assert (
        measurement.id
        == Measurement.model_validate_json(measurement.model_dump_json()).id
    )


@pytest.mark.unit
def test_measurement_value_dataframe():
    measurement = Measurement(unit="%")
    df = pd.DataFrame(
        {
            "A": [1, 1, 2, None, 3],  # 3 unique out of 4 non-null values = 75%
            "B": ["x", "x", "y", "z", None],  # 3 unique out of 4 non-null values = 75%
        }
    )
    result = measurement.call(df)
    # Total: 6 unique values out of 8 non-null values = 75%
    assert result == 75.0
    assert measurement.value == 75.0


@pytest.mark.unit
def test_measurement_value_list():
    measurement = Measurement(unit="%")
    data = [1, 1, 2, None, 3]  # 3 unique out of 4 non-null values = 75%
    result = measurement.call(data)
    assert result == 75.0
    assert measurement.value == 75.0


@pytest.mark.unit
def test_measurement_value_dict():
    measurement = Measurement(unit="%")
    data = {
        "a": 1,
        "b": 1,
        "c": 2,
        "d": None,
        "e": 3,
    }  # 3 unique out of 4 non-null values = 75%
    result = measurement.call(data)
    assert result == 75.0
    assert measurement.value == 75.0


@pytest.mark.unit
def test_measurement_unit():
    measurement = Measurement(unit="%")
    df = pd.DataFrame({"A": [1, 1, 2, 3]})
    measurement.call(df)
    assert measurement.unit == "%"


@pytest.mark.unit
def test_column_distinctiveness():
    measurement = Measurement(unit="%")
    df = pd.DataFrame(
        {
            "A": [1, 1, 2, None, 3],  # 3 unique out of 4 non-null values = 75%
            "B": ["x", "x", "y", "z", None],  # 3 unique out of 4 non-null values = 75%
        }
    )
    column_scores = measurement.get_column_distinctiveness(df)
    assert column_scores["A"] == 75.0
    assert column_scores["B"] == 75.0


@pytest.mark.unit
def test_empty_data():
    measurement = Measurement(unit="%")
    assert measurement.call([]) == 0.0
    assert measurement.call({}) == 0.0
    assert measurement.call(pd.DataFrame()) == 0.0


@pytest.mark.unit
def test_all_null_data():
    measurement = Measurement(unit="%")
    assert measurement.call([None, None]) == 0.0
    assert measurement.call({"a": None, "b": None}) == 0.0
    assert measurement.call(pd.DataFrame({"A": [None, None]})) == 0.0


@pytest.mark.unit
def test_invalid_input():
    measurement = Measurement(unit="%")
    with pytest.raises(ValueError):
        measurement.call("invalid input")
