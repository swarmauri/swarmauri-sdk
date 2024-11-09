import pytest
from swarmauri.measurements.concrete.MiscMeasurement import MiscMeasurement


@pytest.mark.unit
def test_resource():
    def test():
        misc = MiscMeasurement()
        assert misc.resource == "measurement"

    test()


@pytest.mark.unit
def test_type():
    misc = MiscMeasurement()
    assert misc.type == "MiscMeasurement"


@pytest.mark.unit
def test_serialization():
    misc = MiscMeasurement(unit="count", value={"sum": 15, "minimum": 1, "maximum": 5})
    assert misc.id == MiscMeasurement.model_validate_json(misc.model_dump_json()).id


@pytest.mark.unit
def test_measurement_numeric_value():
    def test():
        # Test numeric calculations
        misc = MiscMeasurement()
        data = [1, 2, 3, 4, 5]

        # Test via __call__
        results = misc(data, metric_type="numeric")
        assert results["sum"] == 15
        assert results["minimum"] == 1
        assert results["maximum"] == 5

        # Test that value property is updated
        assert misc.value == results

    test()


@pytest.mark.unit
def test_measurement_string_value():
    def test():
        # Test string calculations
        misc = MiscMeasurement()
        data = ["hello", "world", "python"]

        # Test via __call__
        results = misc(data, metric_type="string")
        assert results["min_length"] == 5  # "hello" and "world"
        assert results["max_length"] == 6  # "python"

        # Test that value property is updated
        assert misc.value == results

    test()


@pytest.mark.unit
def test_measurement_unit():
    def test():
        misc = MiscMeasurement(unit="count")
        assert misc.unit == "count"

    test()


@pytest.mark.unit
def test_individual_calculations():
    def test():
        misc = MiscMeasurement()
        data = [1, 2, 3, 4, 5]

        # Test individual numeric calculations
        assert misc.calculate_sum(data) == 15
        assert misc.calculate_minimum(data) == 1
        assert misc.calculate_maximum(data) == 5

        # Test that _values dictionary is updated
        assert misc._values["sum"] == 15
        assert misc._values["minimum"] == 1
        assert misc._values["maximum"] == 5

    test()


@pytest.mark.unit
def test_invalid_metric_type():
    def test():
        misc = MiscMeasurement()
        data = [1, 2, 3, 4, 5]

        # Test that invalid metric_type raises ValueError
        with pytest.raises(ValueError) as exc_info:
            misc(data, metric_type="invalid")

        assert str(exc_info.value) == "metric_type must be either 'numeric' or 'string'"

    test()


@pytest.mark.unit
def test_pandas_series_support():
    def test():
        import pandas as pd

        misc = MiscMeasurement()

        # Test with pandas Series
        numeric_series = pd.Series([1, 2, 3, 4, 5])
        string_series = pd.Series(["hello", "world", "python"])

        # Test numeric calculations with Series
        numeric_results = misc(numeric_series, metric_type="numeric")
        assert numeric_results["sum"] == 15
        assert numeric_results["minimum"] == 1
        assert numeric_results["maximum"] == 5

        # Test string calculations with Series
        string_results = misc(string_series, metric_type="string")
        assert string_results["min_length"] == 5
        assert string_results["max_length"] == 6

    test()
