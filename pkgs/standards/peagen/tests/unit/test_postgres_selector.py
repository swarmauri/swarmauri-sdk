import shutil
import psycopg2
import pytest

pytest.importorskip("pytest_postgresql")
if shutil.which("pg_ctl") is None:
    pytest.skip("requires PostgreSQL binaries", allow_module_level=True)

from peagen.selectors.postgres_selector import PostgresSelector


@pytest.mark.unit
def test_select_top_k(postgresql):
    if shutil.which("pg_ctl") is None:
        pytest.skip("requires PostgreSQL binaries")
    tbl = "task_results"
    with psycopg2.connect(postgresql.dsn()) as conn, conn.cursor() as cur:
        cur.execute(
            f"CREATE TABLE {tbl} (commit_sha TEXT, fitness FLOAT, created_at TIMESTAMP)"
        )
        for i in range(20):
            cur.execute(f"INSERT INTO {tbl} VALUES ('sha{i}', {i}, NOW())")
        conn.commit()

    sel = PostgresSelector(
        dsn=postgresql.dsn(),
        table=tbl,
        fitness_col="fitness",
        sha_col="commit_sha",
        k=5,
    )
    parents = sel.select()
    assert [p.fitness for p in parents] == [19, 18, 17, 16, 15]
