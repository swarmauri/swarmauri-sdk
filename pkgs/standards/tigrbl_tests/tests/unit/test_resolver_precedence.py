from types import SimpleNamespace

from tigrbl.engine.shortcuts import mem, pga, pgs, prov, sqlitef
from tigrbl.engine import resolver


def test_precedence_op_over_model_over_api_over_app(tmp_path):
    # Build four distinct Providers to track identity
    _app_prov = prov(sqlitef(str(tmp_path / "app.sqlite")))
    _api_prov = prov(pgs(host="db", name="api_db"))
    _model_prov = prov(mem(async_=False))
    _op_prov = prov(pga(host="db", name="op_db"))

    # Fake “api” and “model” identities
    api = SimpleNamespace()

    class Model:
        __name__ = "Model"

    # Register in resolver
    resolver.set_default(sqlitef(str(tmp_path / "app.sqlite")))
    resolver.register_api(
        api, {"kind": "postgres", "async": False, "host": "db", "db": "api_db"}
    )
    resolver.register_table(Model, {"kind": "sqlite", "async": False, "mode": "memory"})
    resolver.register_op(
        Model,
        "create",
        {"kind": "postgres", "async": True, "host": "db", "db": "op_db"},
    )

    # Resolve each level
    p_app = resolver.resolve_provider()
    p_api = resolver.resolve_provider(api=api)
    p_model = resolver.resolve_provider(model=Model)
    p_op = resolver.resolve_provider(model=Model, op_alias="create")

    # Each level should resolve to a different provider with expected sync/async kind
    assert p_app is not None and p_app.kind == "sync"
    assert p_api is not None and p_api is not p_app and p_api.kind == "sync"
    assert p_model is not None and p_model is not p_api and p_model.kind == "sync"
    assert p_op is not None and p_op is not p_model and p_op.kind == "async"

    # Also test acquire() end-to-end
    db, release = resolver.acquire(model=Model, op_alias="create")
    try:
        assert db is not None
    finally:
        release()
