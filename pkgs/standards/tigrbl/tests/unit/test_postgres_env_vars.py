from tigrbl.engine.builders import async_postgres_engine


def test_async_postgres_engine_uses_pg_env(monkeypatch):
    monkeypatch.setenv("PGUSER", "bob")
    monkeypatch.setenv("PGPASSWORD", "pw")
    monkeypatch.setenv("PGHOST", "dbhost")
    monkeypatch.setenv("PGPORT", "5433")
    monkeypatch.setenv("PGDATABASE", "mydb")

    eng, _ = async_postgres_engine()

    assert eng.url.username == "bob"
    assert eng.url.password == "pw"
    assert eng.url.host == "dbhost"
    assert eng.url.port == 5433
    assert eng.url.database == "mydb"
