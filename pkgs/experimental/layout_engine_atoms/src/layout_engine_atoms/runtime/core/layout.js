export function computeGridPlacement(frame, grid, viewport) {
  if (!grid || !frame) {
    return {};
  }

  const columnCount = grid.columns?.length ?? 1;
  const gapX = Number(grid.gap_x ?? 0);
  const gapY = Number(grid.gap_y ?? 0);
  const rowHeight = Number(grid.row_height ?? 0);
  const totalGap = gapX * Math.max(columnCount - 1, 0);
  const viewportWidth = Number(viewport?.width ?? 0);

  const averageColumnWidth =
    columnCount > 0 ? (viewportWidth - totalGap) / columnCount : viewportWidth;
  const stepX = averageColumnWidth + gapX;
  const stepY = rowHeight + gapY;

  const columnStart = Math.round(Number(frame.x ?? 0) / stepX) + 1;
  const rowStart = Math.round(Number(frame.y ?? 0) / stepY) + 1;
  const columnSpan = Math.max(
    1,
    Math.min(
      columnCount,
      Math.round(Number(frame.w ?? 0) / stepX) || 1,
      columnCount - columnStart + 1,
    ),
  );
  const rowSpan = Math.max(
    1,
    rowHeight ? Math.round(Number(frame.h ?? 0) / rowHeight) || 1 : 1,
  );

  return {
    gridColumn: `${columnStart} / span ${columnSpan}`,
    gridRow: `${rowStart} / span ${rowSpan}`,
  };
}
