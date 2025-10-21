export function formatPrimaryValue(value, format) {
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

export function formatDelta(delta) {
  if (delta === null || delta === undefined) {
    return "—";
  }
  const asPercent = (delta * 100).toFixed(Math.abs(delta) >= 0.1 ? 1 : 2);
  const prefix = delta > 0 ? "+" : "";
  return `${prefix}${asPercent}%`;
}

export function escapeHtml(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

export function formatInline(text) {
  const escaped = escapeHtml(text);
  return escaped
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/\*(.+?)\*/g, "<em>$1</em>")
    .replace(/`([^`]+)`/g, "<code>$1</code>");
}

export function markdownToHtml(markdown) {
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
      html.push(`<h3>${formatInline(line.slice(4).trim())}</h3>`);
      continue;
    }
    if (line.startsWith("## ")) {
      closeList();
      html.push(`<h2>${formatInline(line.slice(3).trim())}</h2>`);
      continue;
    }
    if (line.startsWith("# ")) {
      closeList();
      html.push(`<h1>${formatInline(line.slice(2).trim())}</h1>`);
      continue;
    }
    if (line.startsWith("- ") || line.startsWith("* ")) {
      if (!inList) {
        html.push("<ul>");
        inList = true;
      }
      html.push(`<li>${formatInline(line.slice(2).trim())}</li>`);
      continue;
    }

    closeList();
    html.push(`<p>${formatInline(line)}</p>`);
  }

  closeList();
  return html.join("");
}

export function normalizeBarSeries(series) {
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
      maxMagnitude <= 0
        ? 0
        : Math.min(100, (Math.abs(item.value) / maxMagnitude) * 100);
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
