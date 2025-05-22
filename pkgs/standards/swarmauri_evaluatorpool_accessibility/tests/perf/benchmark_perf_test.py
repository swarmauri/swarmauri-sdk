"""Performance benchmarks for swarmauri_evaluatorpool_accessibility.

Run this benchmark in isolation from the pkgs directory:

    cd /workspace/swarmauri-sdk/pkgs
    uv run --package swarmauri_evaluatorpool_accessibility --directory standards/swarmauri_evaluatorpool_accessibility pytest tests/perf
"""

import pytest


@pytest.mark.perf
def test_basic_benchmark(benchmark):
    data = list(range(1000))

    def process():
        [x * x for x in data]

    benchmark(process)
