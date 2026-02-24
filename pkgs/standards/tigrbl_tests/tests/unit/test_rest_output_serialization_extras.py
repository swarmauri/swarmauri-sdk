from types import SimpleNamespace

from pydantic import BaseModel

from tigrbl.bindings.rest.io import _serialize_output
from tigrbl.op import OpSpec


class _OutModel(BaseModel):
    id: str
    digest: str


class _ModelWithSchemas:
    __name__ = "ApiKeyModel"
    schemas = SimpleNamespace(create=SimpleNamespace(out=_OutModel))


def test_serialize_output_preserves_runtime_extras_for_single_item():
    result = {"id": "k1", "digest": "abc", "api_key": "raw-token"}

    out = _serialize_output(
        _ModelWithSchemas,
        alias="create",
        target="create",
        sp=OpSpec(alias="create", target="create"),
        result=result,
    )

    assert out["id"] == "k1"
    assert out["digest"] == "abc"
    assert out["api_key"] == "raw-token"


def test_serialize_output_preserves_runtime_extras_for_list_items():
    result = [
        {"id": "k1", "digest": "abc", "api_key": "raw-1"},
        {"id": "k2", "digest": "def", "api_key": "raw-2"},
    ]

    out = _serialize_output(
        _ModelWithSchemas,
        alias="create",
        target="list",
        sp=OpSpec(alias="create", target="create"),
        result=result,
    )

    assert out[0]["id"] == "k1"
    assert out[0]["api_key"] == "raw-1"
    assert out[1]["id"] == "k2"
    assert out[1]["api_key"] == "raw-2"
