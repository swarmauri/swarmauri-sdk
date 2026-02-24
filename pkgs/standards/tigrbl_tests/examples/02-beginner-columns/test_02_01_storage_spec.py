from __future__ import annotations

from tigrbl.specs import S
from tigrbl.types import Integer


def test_storage_spec_basics() -> None:
    spec = S(type_=Integer, nullable=False, primary_key=True, default=1)
    assert spec.type_ is Integer
    assert spec.nullable is False
    assert spec.primary_key is True
    assert spec.default == 1
