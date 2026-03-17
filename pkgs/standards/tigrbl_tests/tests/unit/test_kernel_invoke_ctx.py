import pytest

from tigrbl_kernel import Kernel


@pytest.mark.asyncio
async def test_kernel_invoke_with_basic_ctx():
    k = Kernel()
    assert not hasattr(k, "invoke")
