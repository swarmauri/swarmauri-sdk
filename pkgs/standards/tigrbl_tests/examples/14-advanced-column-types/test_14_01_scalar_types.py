from __future__ import annotations

from tigrbl.specs import S
from tigrbl.types import Boolean, Integer, Numeric, String


def test_scalar_column_types() -> None:
    assert S(type_=Integer).type_ is Integer
    assert S(type_=String).type_ is String
    assert S(type_=Boolean).type_ is Boolean
    assert S(type_=Numeric).type_ is Numeric
