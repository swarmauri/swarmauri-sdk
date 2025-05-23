import pytest
from swm_example_community_package import ExampleCommunityAgent

@pytest.mark.perf
def test_swm_example_community_package_performance(benchmark):
    instance = ExampleCommunityAgent()
    if hasattr(instance, '__call__'):
        benchmark(lambda: instance('test'))
    elif hasattr(instance, 'parse'):
        benchmark(lambda: instance.parse('test'))
    elif hasattr(instance, 'embed'):
        benchmark(lambda: instance.embed('test'))
    else:
        benchmark(lambda: None)
