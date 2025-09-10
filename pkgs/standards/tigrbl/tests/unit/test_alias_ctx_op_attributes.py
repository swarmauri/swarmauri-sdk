from tigrbl import alias_ctx, alias
from tigrbl.op import resolve


def _spec_for(model: type, target: str):
    """Return OpSpec for canonical verb `target`."""
    return next(sp for sp in resolve(model) if sp.target == target)


def test_alias_ctx_renames_canonical_verb():
    @alias_ctx(read="get")
    class M:
        pass

    spec = _spec_for(M, "read")
    assert spec.alias == "get"


def test_alias_ctx_overrides_request_schema():
    @alias_ctx(read=alias("get", request_schema="Search.in"))
    class M:
        pass

    spec = _spec_for(M, "read")
    assert spec.request_model == "Search.in"


def test_alias_ctx_overrides_response_schema():
    @alias_ctx(read=alias("get", response_schema="Search.out"))
    class M:
        pass

    spec = _spec_for(M, "read")
    assert spec.response_model == "Search.out"


def test_alias_ctx_overrides_persist():
    @alias_ctx(read=alias("get", persist="skip"))
    class M:
        pass

    spec = _spec_for(M, "read")
    assert spec.persist == "skip"


def test_alias_ctx_overrides_arity():
    @alias_ctx(delete=alias("remove", arity="collection"))
    class M:
        pass

    spec = _spec_for(M, "delete")
    assert spec.arity == "collection"


def test_alias_ctx_overrides_rest_exposure():
    @alias_ctx(read=alias("get", rest=False))
    class M:
        pass

    spec = _spec_for(M, "read")
    assert spec.expose_routes is False
