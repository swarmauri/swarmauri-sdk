"""Context-manager authoring API.

Usage:
  from layout_engine.authoring.ctx import TableCtx, render_table, export_table
  from layout_engine.authoring.widgets import Text, Button, Timeseries

  t = TableCtx()
  with t as tbl:
      with tbl.row() as r:
          with r.col("m") as c1:
              c1.add(Text("title", value="Welcome"))
          with r.col("s") as c2:
              c2.add(Button("go", label="Run"))

  html = render_table(t)  # SSR page HTML
"""
from .builder import TableCtx, RowCtx, ColCtx
from .runtime import compile_table, render_table, export_table, serve_table

__all__ = [
    "TableCtx","RowCtx","ColCtx",
    "compile_table","render_table","export_table","serve_table",
]
