import pytest
from swarmauri_tool_jupyterexportpython import JupyterExportPythonTool

@pytest.mark.perf
def test_swarmauri_tool_jupyterexportpython_performance(benchmark):
    instance = JupyterExportPythonTool()
    if hasattr(instance, '__call__'):
        benchmark(lambda: instance('test'))
    elif hasattr(instance, 'parse'):
        benchmark(lambda: instance.parse('test'))
    elif hasattr(instance, 'embed'):
        benchmark(lambda: instance.embed('test'))
    else:
        benchmark(lambda: None)
