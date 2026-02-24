from pathlib import Path

from openpyxl import Workbook

from tigrbl_engine_xlsx import xlsx_engine


def test_xlsx_engine_smoke(tmp_path: Path) -> None:
    path = tmp_path / "demo.xlsx"
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "widgets"
    sheet.append(["id", "name"])
    sheet.append([1, "a"])
    workbook.save(path)

    engine, mk = xlsx_engine(mapping={"path": str(path), "pk": "id"})
    session = mk()
    assert engine.path == str(path)
    assert len(session.table("widgets")) == 1
