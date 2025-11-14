const FALLBACK_EVENT = "layout-engine:svelte:fallback";
const STYLE_ID = "le-svelte-fallback-styles";

function ensureStyles() {
  if (document.getElementById(STYLE_ID)) {
    return;
  }
  const style = document.createElement("style");
  style.id = STYLE_ID;
  style.textContent = `
  .le-fallback-root {
    display: flex;
    flex-direction: column;
    gap: 24px;
  }
  .le-fallback-header {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }
  .le-fallback-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 24px;
  }
  .le-fallback-tile {
    background: rgba(15, 23, 42, 0.92);
    border-radius: 20px;
    border: 1px solid rgba(148, 163, 184, 0.22);
    padding: 24px;
    box-shadow: 0 18px 44px rgba(2, 6, 23, 0.6);
    color: #f5f5f4;
    font-family: "Inter", system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
  }
  .le-fallback-tile h2 {
    margin: 0 0 12px;
    font-size: 1.25rem;
  }
  .le-fallback-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }
  .le-fallback-card {
    padding: 12px 16px;
    border-radius: 12px;
    background: rgba(30, 41, 59, 0.7);
    border: 1px solid rgba(148, 163, 184, 0.18);
  }
  .le-fallback-card h3 {
    margin: 0 0 6px;
    font-size: 1.1rem;
  }
  .le-fallback-metrics {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
    gap: 12px;
  }
  .le-fallback-metric {
    background: rgba(30, 41, 59, 0.7);
    border-radius: 10px;
    padding: 12px;
    text-align: center;
    font-weight: 600;
  }
  .le-fallback-pulse {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  .le-fallback-pill {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    border-radius: 999px;
    padding: 6px 12px;
    background: rgba(59, 130, 246, 0.2);
    font-weight: 500;
  }
  `;
  document.head.appendChild(style);
}

function parseConfig() {
  const el = document.getElementById("le-shell-config");
  if (!el) {
    throw new Error("Unable to locate shell config");
  }
  try {
    return JSON.parse(el.textContent || "{}");
  } catch (error) {
    console.error("Failed to parse shell config", error);
    return {};
  }
}

function resolveManifestUrl(config) {
  const router = config?.router ?? {};
  const base = router.manifestUrl || "./manifest.json";
  const defaultPage = router.defaultPageId || null;
  if (!defaultPage || base.includes("page=")) {
    return base;
  }
  const url = new URL(base, window.location.href);
  url.searchParams.set(router.pageParam || "page", defaultPage);
  return url.toString();
}

async function fetchManifest(config) {
  const manifestUrl = resolveManifestUrl(config);
  const response = await fetch(manifestUrl, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`Manifest request failed: ${response.status} ${response.statusText}`);
  }
  return response.json();
}

function renderHeader(root, config) {
  const headerSlot = config?.ui?.headerSlot;
  if (!headerSlot) {
    return;
  }
  const header = document.createElement("div");
  header.className = "le-fallback-header";
  header.innerHTML = headerSlot;
  root.appendChild(header);
}

function renderCardList(tile) {
  const container = document.createElement("div");
  container.className = "le-fallback-tile";
  const title = document.createElement("h2");
  title.textContent = "Highlights";
  container.appendChild(title);

  const list = document.createElement("div");
  list.className = "le-fallback-list";
  for (const card of tile.props?.cards || []) {
    const cardEl = document.createElement("div");
    cardEl.className = "le-fallback-card";
    if (card.title) {
      const cardTitle = document.createElement("h3");
      cardTitle.textContent = card.title;
      cardEl.appendChild(cardTitle);
    }
    if (card.description) {
      const desc = document.createElement("p");
      desc.style.margin = "0";
      desc.style.opacity = "0.8";
      desc.textContent = card.description;
      cardEl.appendChild(desc);
    }
    list.appendChild(cardEl);
  }
  container.appendChild(list);
  return container;
}

function renderPulse(tile) {
  const container = document.createElement("div");
  container.className = "le-fallback-tile le-fallback-pulse";
  const status = document.createElement("span");
  status.className = "le-fallback-pill";
  status.textContent = (tile.props?.type || "info").toUpperCase();
  container.appendChild(status);
  const message = document.createElement("p");
  message.style.margin = "0";
  message.style.fontSize = "1rem";
  message.textContent = tile.props?.message || "Awaiting updates";
  container.appendChild(message);
  return container;
}

function renderMetrics(tile) {
  const container = document.createElement("div");
  container.className = "le-fallback-tile";
  const title = document.createElement("h2");
  title.textContent = "Metrics";
  container.appendChild(title);
  const grid = document.createElement("div");
  grid.className = "le-fallback-metrics";
  for (const value of tile.props?.data || []) {
    const metric = document.createElement("div");
    metric.className = "le-fallback-metric";
    metric.textContent = String(value);
    grid.appendChild(metric);
  }
  container.appendChild(grid);
  return container;
}

function renderTiles(manifest) {
  const grid = document.createElement("div");
  grid.className = "le-fallback-grid";
  const tiles = Array.isArray(manifest?.tiles) ? manifest.tiles : [];
  for (const tile of tiles) {
    switch (tile.role) {
      case "swarmakit:svelte:cardbased-list":
        grid.appendChild(renderCardList(tile));
        break;
      case "swarmakit:svelte:activity-indicators":
        grid.appendChild(renderPulse(tile));
        break;
      case "swarmakit:svelte:data-summary":
        grid.appendChild(renderMetrics(tile));
        break;
      default: {
        const unknown = document.createElement("div");
        unknown.className = "le-fallback-tile";
        unknown.textContent = `Unsupported tile: ${tile.role}`;
        grid.appendChild(unknown);
      }
    }
  }
  return grid;
}

let fallbackInvoked = false;

async function handleFallback() {
  if (fallbackInvoked) {
    return;
  }
  fallbackInvoked = true;
  try {
    ensureStyles();
    const config = parseConfig();
    const manifest = await fetchManifest(config);
    const target = document.getElementById("le-app");
    if (!target) {
      throw new Error("Fallback: mount element missing");
    }
    target.innerHTML = "";
    const root = document.createElement("div");
    root.className = "le-fallback-root";
    renderHeader(root, config);
    root.appendChild(renderTiles(manifest));
    target.appendChild(root);
  } catch (error) {
    console.error("Svelte fallback rendering failed", error);
  }
}

function install() {
  if (typeof window === "undefined") {
    return;
  }
  window.addEventListener(FALLBACK_EVENT, handleFallback, { once: true });
  window.addEventListener("load", () => {
    if (!fallbackInvoked) {
      handleFallback();
    }
  });
}

install();