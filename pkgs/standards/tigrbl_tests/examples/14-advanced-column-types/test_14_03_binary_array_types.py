from __future__ import annotations

from tigrbl.specs import S
from tigrbl.types import ARRAY, JSONB, LargeBinary


def test_binary_and_array_types() -> None:
    assert S(type_=LargeBinary).type_ is LargeBinary
    assert S(type_=ARRAY).type_ is ARRAY
    assert S(type_=JSONB).type_ is JSONB
