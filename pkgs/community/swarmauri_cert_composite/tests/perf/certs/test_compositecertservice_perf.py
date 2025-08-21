import asyncio


def test_create_csr_perf(benchmark, composite, sample_key):
    async def run():
        await composite.create_csr(sample_key, {"CN": "example"})

    benchmark(lambda: asyncio.run(run()))
