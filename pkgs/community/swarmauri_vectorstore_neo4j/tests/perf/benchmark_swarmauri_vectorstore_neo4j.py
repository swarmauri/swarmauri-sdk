import pytest
from swarmauri_vectorstore_neo4j import Neo4jVectorStore

@pytest.mark.perf
def test_swarmauri_vectorstore_neo4j_performance(benchmark):
    instance = Neo4jVectorStore()
    if hasattr(instance, '__call__'):
        benchmark(lambda: instance('test'))
    elif hasattr(instance, 'parse'):
        benchmark(lambda: instance.parse('test'))
    elif hasattr(instance, 'embed'):
        benchmark(lambda: instance.embed('test'))
    else:
        benchmark(lambda: None)
