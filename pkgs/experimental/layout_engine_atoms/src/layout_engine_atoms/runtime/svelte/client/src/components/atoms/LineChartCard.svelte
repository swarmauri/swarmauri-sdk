<script>
  import { formatPrimaryValue } from "../../core/index.js";

  export let tile = {};

  const palette = ["#57b3ff", "#a385ff", "#59d6a4", "#f6c177"];

  function normalizeSeries(series) {
    const allPoints = (series ?? []).flatMap((entry) => entry?.points ?? []);
    if (!allPoints.length) {
      return { series: [], domain: { min: 0, max: 1 } };
    }

    const min = Math.min(...allPoints.map((point) => point.y));
    const max = Math.max(...allPoints.map((point) => point.y));
    const range = max - min || 1;

    const normalized = (series ?? []).map((entry, seriesIndex) => {
      const points = entry?.points ?? [];
      const normalizedPoints = points.map((point, pointIndex) => {
        const step =
          points.length > 1 ? pointIndex / (points.length - 1) : pointIndex;
        const x = step * 100;
        const y = 90 - ((point.y - min) / range) * 80;
        return { x, y, rawX: point.x, rawY: point.y };
      });

      return {
        label: entry?.label ?? `Series ${seriesIndex + 1}`,
        color: palette[seriesIndex % palette.length],
        points: normalizedPoints,
      };
    });

    return {
      series: normalized,
      domain: { min, max },
    };
  }

  $: props = tile?.props ?? {};
  $: normalized = normalizeSeries(props.series ?? []);
  $: polylineData = normalized.series.map((entry) => ({
    color: entry.color,
    points: entry.points.map((p) => `${p.x},${p.y}`).join(" "),
  }));
  $: latestSnapshot = normalized.series.map((entry) => {
    const last = entry.points.at(-1);
    return {
      label: entry.label,
      color: entry.color,
      value: last?.rawY ?? "—",
    };
  });
</script>

<div class="line-chart">
  <div class="line-chart__header">
    <div>
      <h3 class="metric-card__label" style="margin: 0 0 4px;">
        {props.label}
      </h3>
      {#each latestSnapshot as snapshot (snapshot.label)}
        <div class="dashboard__meta">
          <span
            class="legend-swatch"
            style={`background: ${snapshot.color}`}
          ></span>
          <strong>{snapshot.label}:</strong>
          <span>{formatPrimaryValue(snapshot.value)}</span>
        </div>
      {/each}
    </div>
  </div>
  <div class="line-chart__plot">
    <svg class="line-chart__svg" viewBox="0 0 100 100" preserveAspectRatio="none">
      <defs>
        <linearGradient id="gridGradient" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="rgba(255,255,255,0.08)" />
          <stop offset="100%" stop-color="rgba(255,255,255,0.02)" />
        </linearGradient>
      </defs>
      <rect x="0" y="0" width="100" height="100" fill="url(#gridGradient)" opacity="0.4" />
      {#each polylineData as series (series.color)}
        <polyline
          points={series.points}
          fill="none"
          stroke={series.color}
          stroke-width="2.5"
          stroke-linejoin="round"
          stroke-linecap="round"
        />
      {/each}
    </svg>
  </div>
</div>
