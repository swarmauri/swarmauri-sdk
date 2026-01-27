from __future__ import annotations

from typing import Any, Mapping

from pydantic import BaseModel, Field

from ..core.size import Size
from ..core.tokens import resolve_grid_tokens


class GridTrack(BaseModel):
    """A single grid column track with a Size (px|%|fr)."""

    size: Size


class GridSpec(BaseModel):
    """Explicit grid container description.

    - columns: list of GridTrack defining the column sizing scheme
    - row_height: height of one row unit in pixels
    - gap_x/gap_y: inter-column and inter-row gaps in pixels
    - breakpoints: optional list of (max_width_px, columns_for_that_break)
      The first entry whose max_width >= viewport.width wins.
    """

    columns: list[GridTrack]
    row_height: int = 180
    gap_x: int = 12
    gap_y: int = 12
    baseline_unit: int | None = None
    tokens: Mapping[str, str] = Field(default_factory=dict)
    breakpoints: list[tuple[int, list[GridTrack]]] = Field(default_factory=list)

    @classmethod
    def from_tokens(
        cls,
        tokens: Mapping[str, str],
        *,
        overrides: Mapping[str, Any] | None = None,
    ) -> "GridSpec":
        resolved = resolve_grid_tokens(tokens)
        data: dict[str, Any] = dict(resolved)
        if overrides:
            data.update(overrides)

        columns_data = data.pop("columns", None)
        if columns_data is None:
            raise ValueError("Grid tokens must include a column definition")

        columns: list[GridTrack] = []
        for entry in columns_data:
            if isinstance(entry, GridTrack):
                columns.append(entry)
            elif isinstance(entry, Size):
                columns.append(GridTrack(size=entry))
            else:
                raise TypeError(
                    "columns derived from tokens must be Size or GridTrack instances"
                )

        row_height = int(data.pop("row_height", cls.model_fields["row_height"].default))
        gap_x = int(data.pop("gap_x", cls.model_fields["gap_x"].default))
        gap_y = int(data.pop("gap_y", cls.model_fields["gap_y"].default))
        baseline_unit = data.pop("baseline_unit", None)
        breakpoints = data.pop("breakpoints", [])
        data.pop("tokens", None)

        spec = cls(
            columns=columns,
            row_height=row_height,
            gap_x=gap_x,
            gap_y=gap_y,
            baseline_unit=baseline_unit,
            breakpoints=breakpoints,
            tokens=dict(tokens),
            **data,
        )
        return spec


class GridTile(BaseModel):
    """A tile placement within the grid." """

    tile_id: str
    col: int
    row: int
    col_span: int = 1
    row_span: int = 1
