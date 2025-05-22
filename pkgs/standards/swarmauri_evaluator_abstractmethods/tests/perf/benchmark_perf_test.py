"""Performance benchmarks for swarmauri_evaluator_abstractmethods.

Run this benchmark in isolation from the pkgs directory:

    cd /workspace/swarmauri-sdk/pkgs
    uv run --package swarmauri_evaluator_abstractmethods --directory standards/swarmauri_evaluator_abstractmethods pytest tests/perf
"""

import pytest


@pytest.mark.perf
def test_basic_benchmark(benchmark):
    data = list(range(1000))

    def process():
        [x * x for x in data]

    benchmark(process)
