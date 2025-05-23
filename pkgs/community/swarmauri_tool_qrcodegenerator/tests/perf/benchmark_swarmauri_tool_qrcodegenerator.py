import pytest
from swarmauri_tool_qrcodegenerator import QrCodeGeneratorTool

@pytest.mark.perf
def test_swarmauri_tool_qrcodegenerator_performance(benchmark):
    instance = QrCodeGeneratorTool()
    if hasattr(instance, '__call__'):
        benchmark(lambda: instance('test'))
    elif hasattr(instance, 'parse'):
        benchmark(lambda: instance.parse('test'))
    elif hasattr(instance, 'embed'):
        benchmark(lambda: instance.embed('test'))
    else:
        benchmark(lambda: None)
