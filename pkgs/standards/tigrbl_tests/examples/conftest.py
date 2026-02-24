from __future__ import annotations

import pytest

from tigrbl import Base
from tigrbl.runtime import kernel as runtime_kernel
from tigrbl.schema import builder as v3_builder


def _reset_tigrbl_state() -> None:
    Base.metadata.clear()
    v3_builder._SchemaCache.clear()
    runtime_kernel._default_kernel = runtime_kernel.Kernel()


@pytest.fixture(autouse=True)
def _reset_state():
    _reset_tigrbl_state()
    yield
    _reset_tigrbl_state()
