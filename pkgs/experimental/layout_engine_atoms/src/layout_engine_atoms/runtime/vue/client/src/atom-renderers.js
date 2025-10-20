export function createAtomRenderers(vue) {
  const { computed, defineComponent, h, inject } = vue;
  if (!computed || !defineComponent || !h || !inject) {
    throw new Error(
      "createAtomRenderers requires Vue's computed, defineComponent, h, and inject",
    );
  }

  const palette = ["#57b3ff", "#a385ff", "#59d6a4", "#f6c177"];
  const layoutContextKey = "layout-engine-context";

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

  function escapeHtml(value) {
    return String(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function markdownToHtml(markdown) {
    if (!markdown) {
      return "";
    }

    const lines = String(markdown).split(/\r?\n/);
    const html = [];
    let inList = false;

    const closeList = () => {
      if (inList) {
        html.push("</ul>");
        inList = false;
      }
    };

    for (const raw of lines) {
      const line = raw.trim();
      if (!line) {
        closeList();
        continue;
      }

      if (line.startsWith("### ")) {
        closeList();
        html.push(`<h3>${escapeHtml(line.slice(4).trim())}</h3>`);
        continue;
      }
      if (line.startsWith("## ")) {
        closeList();
        html.push(`<h2>${escapeHtml(line.slice(3).trim())}</h2>`);
        continue;
      }
      if (line.startsWith("# ")) {
        closeList();
        html.push(`<h1>${escapeHtml(line.slice(2).trim())}</h1>`);
        continue;
      }
      if (line.startsWith("- ") || line.startsWith("* ")) {
        if (!inList) {
          html.push("<ul>");
          inList = true;
        }
        html.push(`<li>${escapeHtml(line.slice(2).trim())}</li>`);
        continue;
      }

      closeList();
      html.push(`<p>${escapeHtml(line)}</p>`);
    }

    closeList();
    return html.join("");
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

  const MarkdownPanel = defineComponent({
    name: "MarkdownPanel",
    props: {
      tile: { type: Object, required: true },
    },
    setup(props) {
      const title = computed(() => props.tile?.props?.title ?? "");
      const bodyHtml = computed(() =>
        markdownToHtml(props.tile?.props?.body ?? ""),
      );

      return {
        title,
        bodyHtml,
      };
    },
    template: `
      <div class="markdown-panel">
        <h3 v-if="title" class="markdown-panel__title">{{ title }}</h3>
        <div class="markdown-panel__body" v-html="bodyHtml"></div>
      </div>
    `,
  });

  function normalizeBarSeries(series) {
    const entries = Array.isArray(series) ? series : [];
    const normalized = entries
      .map((entry, idx) => {
        const rawValue =
          typeof entry === "number"
            ? entry
            : Number(entry?.value ?? entry?.amount ?? entry?.count ?? NaN);
        if (!Number.isFinite(rawValue)) {
          return null;
        }
        const label =
          (entry && (entry.label ?? entry.name ?? entry.segment)) ??
          `Item ${idx + 1}`;
        const annotation =
          entry && (entry.annotation ?? entry.caption ?? entry.note ?? null);
        return { label, value: rawValue, annotation };
      })
      .filter(Boolean);
    if (!normalized.length) {
      return [];
    }
    const maxMagnitude = Math.max(
      ...normalized.map((item) => Math.abs(item.value)),
    );
    return normalized.map((item) => {
      const percent =
        maxMagnitude <= 0 ? 0 : Math.min(100, (Math.abs(item.value) / maxMagnitude) * 100);
      const valueLabel = new Intl.NumberFormat("en-US", {
        maximumFractionDigits: Math.abs(item.value) >= 100 ? 0 : 1,
      }).format(item.value);
      return {
        label: item.label,
        value: item.value,
        annotation: item.annotation,
        percent,
        valueLabel,
      };
    });
  }

  const HorizontalBarCard = defineComponent({
    name: "HorizontalBarCard",
    props: {
      tile: { type: Object, required: true },
    },
    setup(props) {
      const heading = computed(() => props.tile?.props?.label ?? "");
      const items = computed(() =>
        normalizeBarSeries(props.tile?.props?.series ?? []),
      );
      return {
        heading,
        items,
      };
    },
    template: `
      <div class="bar-card">
        <h3 v-if="heading" class="bar-card__title">{{ heading }}</h3>
        <div v-for="item in items" :key="item.label" class="bar-card__row">
          <div class="bar-card__row-header">
            <span class="bar-card__label">{{ item.label }}</span>
            <span class="bar-card__value">{{ item.valueLabel }}</span>
          </div>
          <div class="bar-card__bar">
            <div class="bar-card__bar-fill" :style="{ width: item.percent + '%' }"></div>
          </div>
          <p v-if="item.annotation" class="bar-card__annotation">{{ item.annotation }}</p>
        </div>
        <p v-if="!items.length" class="bar-card__empty">No segment data available.</p>
      </div>
    `,
  });

  const NavButton = defineComponent({
    name: "LayoutNavButton",
    props: {
      tile: { type: Object, required: true },
    },
    setup(props) {
      const layoutCtx = inject(layoutContextKey, null);
      const roleVariant = computed(() =>
        (props.tile?.role ?? "").endsWith("secondary") ? "secondary" : null,
      );
      const variant = computed(
        () => props.tile?.props?.variant ?? roleVariant.value ?? "primary",
      );
      const label = computed(() => props.tile?.props?.label ?? "Navigate");
      const caption = computed(() => props.tile?.props?.caption ?? "");

      function handleClick(event) {
        event?.preventDefault?.();
        const targetPage =
          props.tile?.props?.targetPage ?? props.tile?.props?.page ?? null;
        if (targetPage && layoutCtx?.setPage) {
          layoutCtx.setPage(targetPage);
        }
        const href = props.tile?.props?.href ?? null;
        if (href) {
          const target = props.tile?.props?.target ?? "_blank";
          if (typeof window !== "undefined" && window.open) {
            window.open(href, target);
          }
        }
        if (layoutCtx?.sendEvent) {
          layoutCtx.sendEvent({
            type: "ui:button.click",
            tile_id: props.tile?.id,
            target_page: targetPage,
            href,
          });
        }
      }

      const buttonClasses = computed(() => ({
        "nav-button": true,
        "nav-button--secondary": variant.value === "secondary",
      }));

      return {
        handleClick,
        buttonClasses,
        label,
        caption,
      };
    },
    template: `
      <button class="nav-button" :class="buttonClasses" type="button" @click="handleClick">
        <span class="nav-button__label">{{ label }}</span>
        <span v-if="caption" class="nav-button__caption">{{ caption }}</span>
      </button>
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
    "viz:panel:markdown": MarkdownPanel,
    "viz:bar:horizontal": HorizontalBarCard,
    "viz:timeseries:line": LineChartCard,
    "viz:table:basic": TableCard,
    "ui:button:primary": NavButton,
    "ui:button:secondary": NavButton,
    default: PlaceholderCard,
  };
}
