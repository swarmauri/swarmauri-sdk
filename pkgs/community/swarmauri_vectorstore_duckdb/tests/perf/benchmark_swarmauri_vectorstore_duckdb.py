import pytest
from swarmauri_vectorstore_duckdb import DuckDBVectorStore

@pytest.mark.perf
def test_swarmauri_vectorstore_duckdb_performance(benchmark):
    instance = DuckDBVectorStore()
    if hasattr(instance, '__call__'):
        benchmark(lambda: instance('test'))
    elif hasattr(instance, 'parse'):
        benchmark(lambda: instance.parse('test'))
    elif hasattr(instance, 'embed'):
        benchmark(lambda: instance.embed('test'))
    else:
        benchmark(lambda: None)
