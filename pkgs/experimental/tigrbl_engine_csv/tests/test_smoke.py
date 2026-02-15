from pathlib import Path

from tigrbl_engine_csv import csv_engine


def test_csv_engine_smoke(tmp_path: Path) -> None:
    csv_path = tmp_path / "example.csv"
    csv_path.write_text("id,value\n1,3\n2,5\n", encoding="utf-8")

    engine, session_factory = csv_engine(
        mapping={"path": str(csv_path), "table": "example", "pk": "id"}
    )
    session = session_factory()

    assert engine.table == "example"
    assert session.query("value > 3").shape == (1, 2)
