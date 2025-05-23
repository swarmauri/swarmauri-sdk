import pytest
from swarmauri_measurement_tokencountestimator import TokenCountEstimatorMeasurement

@pytest.mark.perf
def test_swarmauri_measurement_tokencountestimator_performance(benchmark):
    instance = TokenCountEstimatorMeasurement()
    if hasattr(instance, '__call__'):
        benchmark(lambda: instance('test'))
    elif hasattr(instance, 'parse'):
        benchmark(lambda: instance.parse('test'))
    elif hasattr(instance, 'embed'):
        benchmark(lambda: instance.embed('test'))
    else:
        benchmark(lambda: None)
