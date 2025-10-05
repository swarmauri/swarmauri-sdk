from __future__ import annotations
from typing import Mapping, Any
from .spec import Table, Row, Column, Block
from ..core.size import SizeToken

def to_dict(tbl: Table) -> dict:
    """Serialize Table → plain dict (JSON-friendly)."""
    return {
        "gap_x": tbl.gap_x,
        "gap_y": tbl.gap_y,
        "rows": [
            {
                "height_rows": r.height_rows,
                "columns": [
                    {
                        "size": c.size.value,
                        "blocks": [{"tile_id": b.tile_id, "col_span": b.col_span, "row_span": b.row_span} for b in c.blocks],
                    }
                    for c in r.columns
                ],
            }
            for r in tbl.rows
        ],
    }

def from_dict(obj: Mapping[str, Any]) -> Table:
    """Deserialize Table from a plain dict produced by to_dict."""
    rows = []
    for r in obj.get("rows", []):
        cols = []
        for c in r.get("columns", []):
            blocks = [Block(tile_id=str(b["tile_id"]), col_span=int(b.get("col_span",1)), row_span=int(b.get("row_span",1)))
                      for b in c.get("blocks", [])]
            cols.append(Column(size=SizeToken(str(c["size"])), blocks=tuple(blocks)))
        rows.append(Row(columns=tuple(cols), height_rows=int(r.get("height_rows", 1))))
    return Table(rows=tuple(rows), gap_x=int(obj.get("gap_x", 12)), gap_y=int(obj.get("gap_y", 12)))
