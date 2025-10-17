export function createAtomRenderers(vue) {
  const { computed, defineComponent, h } = vue;
  if (!computed || !defineComponent || !h) {
    throw new Error("createAtomRenderers requires Vue's computed, defineComponent, and h");
  }

  const palette = ["#57b3ff", "#a385ff", "#59d6a4", "#f6c177"];

  function formatPrimaryValue(value, format) {
    if (format === "currency_compact" && typeof value === "number") {
      return new Intl.NumberFormat("en-US", {
        style: "currency",
        currency: "USD",
        notation: "compact",
        maximumFractionDigits: value >= 100 ? 1 : 2,
      }).format(value);
    }

    if (typeof value === "number" && value < 1) {
      return `${(value * 100).toFixed(1)}%`;
    }

    if (typeof value === "number") {
      return new Intl.NumberFormat("en-US", {
        maximumFractionDigits: 1,
      }).format(value);
    }

    return value ?? "—";
  }

  function formatDelta(delta) {
    if (delta === null || delta === undefined) {
      return "—";
    }
    const asPercent = (delta * 100).toFixed(Math.abs(delta) >= 0.1 ? 1 : 2);
    const prefix = delta > 0 ? "+" : "";
    return `${prefix}${asPercent}%`;
  }

  function pickColor(index) {
    return palette[index % palette.length];
  }

  const MetricCard = defineComponent({
    name: "MetricCard",
    props: {
      tile: { type: Object, required: true },
    },
    setup(props) {
      const formattedValue = computed(() =>
        formatPrimaryValue(props.tile?.props?.value, props.tile?.props?.format),
      );
      const deltaLabel = computed(() => formatDelta(props.tile?.props?.delta));
      const isNegative = computed(() => (props.tile?.props?.delta ?? 0) < 0);
      const trendIcon = computed(() => {
        const trend = props.tile?.props?.trend;
        if (trend === "down") {
          return "▼";
        }
        if (trend === "flat") {
          return "◆";
        }
        return "▲";
      });

      return {
        formattedValue,
        deltaLabel,
        isNegative,
        trendIcon,
      };
    },
    template: `
      <div class="metric-card">
        <div class="metric-card__label">{{ tile.props.label }}</div>
        <div class="metric-card__value">{{ formattedValue }}</div>
        <div class="metric-card__delta" :class="{ negative: isNegative }">
          <span>{{ trendIcon }}</span>
          <span>{{ deltaLabel }}</span>
        </div>
        <div class="metric-card__footnote">vs {{ tile.props.period }}</div>
      </div>
    `,
  });

  function normalizeSeries(series) {
    const allPoints = series.flatMap((s) => s.points || []);
    if (!allPoints.length) {
      return { series: [], domain: { min: 0, max: 1 } };
    }

    const min = Math.min(...allPoints.map((p) => p.y));
    const max = Math.max(...allPoints.map((p) => p.y));
    const range = max - min || 1;

    const normalized = series.map((entry, idx) => {
      const points = entry.points || [];
      const normalizedPoints = points.map((point, pointIdx) => {
        const step =
          points.length > 1 ? pointIdx / (points.length - 1) : pointIdx;
        const x = step * 100;
        const y = 90 - ((point.y - min) / range) * 80;
        return { x, y, rawX: point.x, rawY: point.y };
      });
      return {
        label: entry.label ?? `Series ${idx + 1}`,
        color: pickColor(idx),
        points: normalizedPoints,
      };
    });

    return { series: normalized, domain: { min, max } };
  }

  const LineChartCard = defineComponent({
    name: "LineChartCard",
    props: {
      tile: { type: Object, required: true },
    },
    setup(props) {
      const normalized = computed(() =>
        normalizeSeries(props.tile?.props?.series ?? []),
      );

      const polylineData = computed(() =>
        normalized.value.series.map((entry) => ({
          color: entry.color,
          points: entry.points.map((p) => `${p.x},${p.y}`).join(" "),
        })),
      );

      const latestSnapshot = computed(() =>
        normalized.value.series.map((entry) => {
          const last = entry.points.at(-1);
          return {
            label: entry.label,
            color: entry.color,
            value: last?.rawY ?? "—",
          };
        }),
      );

      return {
        normalized,
        polylineData,
        latestSnapshot,
        formatPrimaryValue,
      };
    },
    template: `
      <div class="line-chart">
        <div class="line-chart__header">
          <div>
            <h3 class="metric-card__label" style="margin: 0 0 4px;">{{ tile.props.label }}</h3>
            <div v-for="snapshot in latestSnapshot" :key="snapshot.label" class="dashboard__meta">
              <span class="legend-swatch" :style="{ background: snapshot.color }"></span>
              <strong>{{ snapshot.label }}:</strong>
              <span>{{ formatPrimaryValue(snapshot.value) }}</span>
            </div>
          </div>
        </div>
        <div class="line-chart__plot">
          <svg class="line-chart__svg" viewBox="0 0 100 100" preserveAspectRatio="none">
            <defs>
              <linearGradient id="gridGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stop-color="rgba(255,255,255,0.08)"></stop>
                <stop offset="100%" stop-color="rgba(255,255,255,0.02)"></stop>
              </linearGradient>
            </defs>
            <rect x="0" y="0" width="100" height="100" fill="url(#gridGradient)" opacity="0.4" />
            <polyline
              v-for="series in polylineData"
              :key="series.color"
              :points="series.points"
              fill="none"
              :stroke="series.color"
              stroke-width="2.5"
              stroke-linejoin="round"
              stroke-linecap="round"
            />
          </svg>
        </div>
      </div>
    `,
  });

  const TableCard = defineComponent({
    name: "TableCard",
    props: {
      tile: { type: Object, required: true },
    },
    setup(props) {
      const columns = computed(() => props.tile?.props?.columns ?? []);
      const rows = computed(() => props.tile?.props?.rows ?? []);

      return { columns, rows };
    },
    template: `
      <div class="table-card">
        <h3 class="table-card__title">{{ tile.props.label }}</h3>
        <table class="table-card__table">
          <thead>
            <tr>
              <th v-for="column in columns" :key="column.key">{{ column.name }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in rows" :key="row.account + row.owner">
              <td v-for="column in columns" :key="column.key">{{ row[column.key] }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    `,
  });

  const PlaceholderCard = defineComponent({
    name: "PlaceholderCard",
    props: {
      tile: { type: Object, required: true },
    },
    setup(props) {
      return () =>
        h("div", { class: "placeholder-card" }, [
          h("h3", { class: "table-card__title" }, [
            "Missing renderer for ",
            props.tile.role,
          ]),
          h(
            "pre",
            null,
            JSON.stringify(props.tile.props ?? {}, null, 2),
          ),
        ]);
    },
  });

  return {
    "viz:metric:kpi": MetricCard,
    "viz:timeseries:line": LineChartCard,
    "viz:table:basic": TableCard,
    default: PlaceholderCard,
  };
}
