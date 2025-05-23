import pytest
from swarmauri_tool_jupyterstartkernel import JupyterStartKernelTool

@pytest.mark.perf
def test_swarmauri_tool_jupyterstartkernel_performance(benchmark):
    instance = JupyterStartKernelTool()
    if hasattr(instance, '__call__'):
        benchmark(lambda: instance('test'))
    elif hasattr(instance, 'parse'):
        benchmark(lambda: instance.parse('test'))
    elif hasattr(instance, 'embed'):
        benchmark(lambda: instance.embed('test'))
    else:
        benchmark(lambda: None)
