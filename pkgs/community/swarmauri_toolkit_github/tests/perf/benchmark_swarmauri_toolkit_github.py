import pytest
from swarmauri_toolkit_github import GithubIssueTool

@pytest.mark.perf
def test_swarmauri_toolkit_github_performance(benchmark):
    instance = GithubIssueTool()
    if hasattr(instance, '__call__'):
        benchmark(lambda: instance('test'))
    elif hasattr(instance, 'parse'):
        benchmark(lambda: instance.parse('test'))
    elif hasattr(instance, 'embed'):
        benchmark(lambda: instance.embed('test'))
    else:
        benchmark(lambda: None)
