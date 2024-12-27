import pytest
import pandas as pd
from swarmauri.measurements.concrete.CompletenessMeasurement import (
    CompletenessMeasurement as Measurement,
)


@pytest.mark.unit
def test_ubc_resource():
    def test():
        assert Measurement().resource == "Measurement"

    test()


@pytest.mark.unit
def test_ubc_type():
    measurement = Measurement()
    assert measurement.type == "CompletenessMeasurement"


@pytest.mark.unit
def test_serialization():
    measurement = Measurement()
    assert (
        measurement.id
        == Measurement.model_validate_json(measurement.model_dump_json()).id
    )


@pytest.mark.unit
def test_measurement_unit():
    def test():
        assert Measurement().unit == "%"

    test()


@pytest.mark.unit
def test_measurement_value():
    def test():
        # Test with list
        data_list = ["a", "b", None, "d"]
        measurement = Measurement()
        assert measurement(data_list) == 75.0  # 3 out of 4 values are complete
        assert measurement.value == 75.0

        # Test with dictionary
        data_dict = {"a": 1, "b": None, "c": 3}
        measurement = Measurement()
        expected_value = 66.66666666666667
        assert (
            abs(measurement(data_dict) - expected_value) < 1e-10
        )  # Using absolute difference
        assert abs(measurement.value - expected_value) < 1e-10

        # Test with DataFrame
        df = pd.DataFrame({"col1": ["a", "b", None], "col2": [1, None, 3]})
        measurement = Measurement()
        assert (
            abs(measurement(df) - expected_value) < 1e-10
        )  # 4 out of 6 values are complete
        assert abs(measurement.value - expected_value) < 1e-10

    test()


@pytest.mark.unit
def test_column_completeness():
    def test():
        df = pd.DataFrame(
            {
                "col1": ["a", "b", None],  # 66.67% complete
                "col2": [1, None, 3],  # 66.67% complete
            }
        )
        measurement = Measurement()
        column_scores = measurement.get_column_completeness(df)
        expected_value = 66.66666666666667
        assert abs(column_scores["col1"] - expected_value) < 1e-10
        assert abs(column_scores["col2"] - expected_value) < 1e-10

    test()


@pytest.mark.unit
def test_empty_input():
    def test():
        # Test empty list
        assert Measurement()([]) == 0.0

        # Test empty dict
        assert Measurement()({}) == 0.0

        # Test empty DataFrame
        assert Measurement()(pd.DataFrame()) == 0.0

    test()


@pytest.mark.unit
def test_invalid_input():
    def test():
        measurement = Measurement()
        with pytest.raises(ValueError):
            measurement(42)  # Invalid input type

        with pytest.raises(ValueError):
            measurement.get_column_completeness(
                [1, 2, 3]
            )  # Invalid input for column completeness

    test()
