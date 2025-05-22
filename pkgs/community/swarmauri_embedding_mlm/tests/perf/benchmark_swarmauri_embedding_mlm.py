import pytest
from swarmauri_embedding_mlm import MlmEmbedding

@pytest.mark.perf
def test_swarmauri_embedding_mlm_performance(benchmark):
    instance = MlmEmbedding()
    if hasattr(instance, '__call__'):
        benchmark(lambda: instance('test'))
    elif hasattr(instance, 'parse'):
        benchmark(lambda: instance.parse('test'))
    elif hasattr(instance, 'embed'):
        benchmark(lambda: instance.embed('test'))
    else:
        benchmark(lambda: None)
