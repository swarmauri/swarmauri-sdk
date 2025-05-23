import pytest
from swarmauri_base.DynamicBase import SubclassUnion

@pytest.mark.perf
def test_typing_performance(benchmark):
    result = benchmark(lambda: issubclass(SubclassUnion[list], type))
    assert result is not None  # replace with real condition
