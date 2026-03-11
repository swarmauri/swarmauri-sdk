import pytest

pytestmark = pytest.mark.skip(reason="_in_tx removed in refactor")


@pytest.mark.asyncio
async def test_in_tx_detects_async_session_transaction():
    pass
