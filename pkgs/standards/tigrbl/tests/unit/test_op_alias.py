from pydantic import BaseModel

from tigrbl import op_alias
from tigrbl.op import resolve


def _get_spec(**decorator_kwargs):
    @op_alias(**decorator_kwargs)
    class Model:
        pass

    specs = resolve(Model)
    for sp in specs:
        if (
            sp.alias == decorator_kwargs["alias"]
            and sp.target == decorator_kwargs["target"]
        ):
            return sp
    raise AssertionError("spec not found")


def test_op_alias_sets_alias():
    spec = _get_spec(alias="fetch", target="custom")
    assert spec.alias == "fetch"


def test_op_alias_sets_target():
    spec = _get_spec(alias="do_delete", target="delete")
    assert spec.target == "delete"


def test_op_alias_sets_arity():
    spec = _get_spec(alias="member_op", target="custom", arity="member")
    assert spec.arity == "member"


def test_op_alias_sets_persist():
    spec = _get_spec(alias="persist_op", target="custom", persist="override")
    assert spec.persist == "override"


def test_op_alias_sets_request_model():
    class Req(BaseModel):
        q: int

    spec = _get_spec(alias="req_op", target="custom", request_model=Req)
    assert spec.request_model is Req


def test_op_alias_sets_response_model():
    class Res(BaseModel):
        x: int

    spec = _get_spec(alias="res_op", target="custom", response_model=Res)
    assert spec.response_model is Res


def test_op_alias_sets_http_methods():
    spec = _get_spec(alias="http_op", target="custom", http_methods=("GET", "POST"))
    assert spec.http_methods == ("GET", "POST")


def test_op_alias_sets_tags():
    spec = _get_spec(alias="tag_op", target="custom", tags=("a", "b"))
    assert spec.tags == ("a", "b")


def test_op_alias_sets_rbac_guard_op():
    spec = _get_spec(alias="rbac_op", target="custom", rbac_guard_op="read")
    assert spec.rbac_guard_op == "read"
