import asyncio

from swarmauri_keyprovider_file.examples.basic_usage import run_example


def test_basic_usage_example() -> None:
    kid = asyncio.run(run_example())
    assert isinstance(kid, str)
    assert kid
