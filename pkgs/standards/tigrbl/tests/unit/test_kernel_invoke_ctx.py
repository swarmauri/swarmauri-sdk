import pytest

from tigrbl.runtime.kernel import Kernel


@pytest.mark.asyncio
async def test_kernel_invoke_with_basic_ctx():
    k = Kernel()

    class Model:
        pass

    result = await k.invoke(model=Model, alias="read", db=None, request=None, ctx={})
    assert result is None
