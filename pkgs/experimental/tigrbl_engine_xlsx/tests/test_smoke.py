from pathlib import Path

import pandas as pd

from tigrbl_engine_xlsx import xlsx_engine


def test_xlsx_engine_smoke(tmp_path: Path) -> None:
    path = tmp_path / "demo.xlsx"
    with pd.ExcelWriter(path) as writer:
        pd.DataFrame({"id": [1], "name": ["a"]}).to_excel(
            writer, index=False, sheet_name="widgets"
        )

    engine, mk = xlsx_engine(mapping={"path": str(path), "pk": "id"})
    session = mk()
    assert engine.path == str(path)
    assert session.table("widgets").shape == (1, 2)
