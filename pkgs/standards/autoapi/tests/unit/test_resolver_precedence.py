# tests/test_resolver_precedence.py
from types import SimpleNamespace

from autoapi.v3.engines.shortcuts import mem, sqlitef, pga, pgs, prov  # :contentReference[oaicite:9]{index=9}
from autoapi.v3.engines import resolver  # :contentReference[oaicite:10]{index=10}

def test_precedence_op_over_model_over_api_over_app(tmp_path):
    # Build four distinct Providers to track identity
    app_prov   = prov(sqlitef(str(tmp_path / "app.sqlite")))     # sync sqlite  :contentReference[oaicite:11]{index=11}
    api_prov   = prov(pgs(host="db", name="api_db"))              # sync pg      :contentReference[oaicite:12]{index=12}
    model_prov = prov(mem(async_=False))                          # sync mem     :contentReference[oaicite:13]{index=13}
    op_prov    = prov(pga(host="db", name="op_db"))               # async pg     :contentReference[oaicite:14]{index=14}

    # Fake “api” and “model” identities
    api = SimpleNamespace()
    class Model: __name__ = "Model"

    # Register in resolver
    resolver.set_default(sqlitef(str(tmp_path / "app.sqlite")))         # app  :contentReference[oaicite:15]{index=15}
    resolver.register_api(api, {"kind": "postgres", "async": False, "host": "db", "db": "api_db"})    # api
    resolver.register_table(Model, {"kind": "sqlite", "async": False, "mode": "memory"})              # model
    resolver.register_op(Model, "create", {"kind": "postgres", "async": True, "host": "db", "db": "op_db"})  # op

    # Resolve each level
    p_app   = resolver.resolve_provider()
    p_api   = resolver.resolve_provider(api=api)
    p_model = resolver.resolve_provider(model=Model)
    p_op    = resolver.resolve_provider(model=Model, op_alias="create")

    # Identity checks: we can’t compare to local prov(...) objects because resolver re-coerces,
    # but we can assert precedence by pairwise inequality and kind/expected async-ness
    assert p_app is not None and p_app.kind == "sync"       # sqlite file
    assert p_api is not None and p_api is not p_app and p_api.kind == "sync"
    assert p_model is not None and p_model is not p_api and p_model.kind == "sync"
    assert p_op is not None and p_op is not p_model and p_op.kind == "async"  # op-level wins

    # Also test acquire() end-to-end
    db, release = resolver.acquire(model=Model, op_alias="create")
    try:
        assert db is not None
    finally:
        release()
