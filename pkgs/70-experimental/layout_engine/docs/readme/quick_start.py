from layout_engine import (
    AtomRegistry,
    AtomSpec,
    SizeToken,
    TileSpec,
    Viewport,
    block,
    col,
    quick_manifest_from_table,
    row,
    table,
)
from layout_engine.targets.media import HtmlExporter

atoms = AtomRegistry()
atoms.register(AtomSpec(role="stat", module="@demo/metric"))

tiles = [
    TileSpec(
        id="stat_revenue",
        role="stat",
        props={"label": "Revenue", "value": "$1.2M"},
    ),
    TileSpec(
        id="stat_growth",
        role="stat",
        props={"label": "Growth", "value": "18%"},
    ),
]

layout = table(
    row(
        col(block("stat_revenue"), size=SizeToken.m),
        col(block("stat_growth"), size=SizeToken.m),
    )
)

manifest = quick_manifest_from_table(
    layout,
    Viewport(width=960, height=540),
    tiles,
    atoms_registry=atoms,
)

HtmlExporter(title="Stats Overview").export(manifest, out="stats.html")
