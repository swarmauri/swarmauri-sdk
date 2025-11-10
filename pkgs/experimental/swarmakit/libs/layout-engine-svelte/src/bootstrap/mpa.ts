import ShellApp from "./ShellApp.svelte";
import { createLayoutEngineApp } from "../composables";
import type { LayoutEngineApp } from "../composables";
import { loadManifest } from "../loader";
import type { AtomRegistryMap, LayoutManifest } from "../types";

const CONFIG_ELEMENT_ID = "le-shell-config";
const NAV_EVENT = "layout-engine:navigate";
const CHANNEL_EVENT = "layout-engine:channel";

type RouterConfig = {
  manifestUrl: string;
  pageParam: string;
  defaultPageId: string | null;
  history: "history" | "hash";
  enableMultipage: boolean;
  hydrateThemeFromManifest: boolean;
};

type ManifestEntry = {
  manifest: LayoutManifest;
  components: AtomRegistryMap;
};

const manifestCache = new Map<string, ManifestEntry>();

function loadConfig(): any {
  const el = document.getElementById(CONFIG_ELEMENT_ID);
  if (!el) {
    throw new Error("Missing layout engine config payload");
  }
  return JSON.parse(el.textContent || "{}");
}

function toWsUrl(path: string | undefined): string | null {
  if (!path) return null;
  if (path.startsWith("ws://") || path.startsWith("wss://")) {
    return path;
  }
  const scheme = window.location.protocol === "https:" ? "wss" : "ws";
  return `${scheme}://${window.location.host}${path.startsWith("/") ? path : `/${path}`}`;
}

function normalizeRouterConfig(raw: any): RouterConfig {
  const pageParam = raw?.pageParam ?? "page";
  const defaultPageId = raw?.defaultPageId ?? null;
  return {
    manifestUrl: raw?.manifestUrl ?? "./manifest.json",
    pageParam,
    defaultPageId,
    history: raw?.history === "hash" ? "hash" : "history",
    enableMultipage: Boolean(raw?.enableMultipage || pageParam || defaultPageId),
    hydrateThemeFromManifest: raw?.hydrateThemeFromManifest ?? true,
  };
}

function withPageParam(url: string, pageId: string | null, router: RouterConfig): string {
  if (!router.enableMultipage || !router.pageParam) {
    return url;
  }
  const [base, query = ""] = url.split("?");
  const params = new URLSearchParams(query);
  if (pageId) {
    params.set(router.pageParam, pageId);
  } else {
    params.delete(router.pageParam);
  }
  const qs = params.toString();
  return qs ? `${base}?${qs}` : base;
}

function currentPageFromLocation(router: RouterConfig): string | null {
  if (!router.enableMultipage) return null;
  if (router.history === "hash") {
    const hash = window.location.hash.replace(/^#/, "");
    return hash || null;
  }
  const params = new URLSearchParams(window.location.search);
  return params.get(router.pageParam) || null;
}

function updateLocation(router: RouterConfig, pageId: string | null, opts?: { replace?: boolean }) {
  if (!router.enableMultipage) return;
  const replace = opts?.replace ?? false;
  if (router.history === "hash") {
    const hash = pageId ? `#${pageId}` : "";
    if (replace) {
      const url = `${window.location.pathname}${window.location.search}${hash}`;
      window.history.replaceState({ pageId }, "", url);
    } else {
      window.location.hash = hash;
    }
    return;
  }
  const url = new URL(window.location.href);
  if (pageId) {
    url.searchParams.set(router.pageParam, pageId);
  } else {
    url.searchParams.delete(router.pageParam);
  }
  if (replace) {
    window.history.replaceState({ pageId }, "", url);
  } else {
    window.history.pushState({ pageId }, "", url);
  }
}

function cloneEntry(entry: ManifestEntry): ManifestEntry {
  const manifestClone = typeof structuredClone === "function"
    ? structuredClone(entry.manifest)
    : JSON.parse(JSON.stringify(entry.manifest));
  const componentsClone = new Map(entry.components);
  return { manifest: manifestClone, components: componentsClone };
}

async function fetchManifestForPage(
  router: RouterConfig,
  pageId: string | null,
): Promise<ManifestEntry> {
  const cacheKey = pageId || "__default__";
  if (manifestCache.has(cacheKey)) {
    return cloneEntry(manifestCache.get(cacheKey)!);
  }
  const url = withPageParam(router.manifestUrl, pageId, router);
  const result = await loadManifest(url);
  const entry: ManifestEntry = {
    manifest: result.manifest,
    components: result.components,
  };
  manifestCache.set(cacheKey, entry);
  return cloneEntry(entry);
}

async function bootstrap() {
  const mountEl = document.getElementById("le-app");
  if (!mountEl) {
    throw new Error("Unable to find mount element '#le-app'");
  }

  const config = loadConfig();
  const routerConfig = normalizeRouterConfig(config.router ?? {});
  const realtimeConfig = config.realtime ?? {};
  const muxUrl = realtimeConfig.enabled ? toWsUrl(realtimeConfig.path) : null;

  const initialPageId = routerConfig.enableMultipage
    ? currentPageFromLocation(routerConfig) ?? routerConfig.defaultPageId
    : null;

  const app: LayoutEngineApp = await createLayoutEngineApp({
    manifestUrl: withPageParam(routerConfig.manifestUrl, initialPageId, routerConfig),
    muxUrl: muxUrl || undefined,
  });

  const shell = new ShellApp({
    target: mountEl,
    props: {
      manifestStore: app.manifest,
      registryStore: app.components,
      mux: app.mux,
      headerSlot: config.ui?.headerSlot ?? null,
      contentSlot: config.ui?.contentSlot ?? null,
      footerSlot: config.ui?.footerSlot ?? null,
    },
  });

  const applyManifest = (entry: ManifestEntry) => {
    app.manifest.set(entry.manifest);
    app.components.set(entry.components);
  };

  const handleNavigate = async (pageId: string | null, pushHistory = true) => {
    const entry = await fetchManifestForPage(routerConfig, pageId);
    applyManifest(entry);
    if (routerConfig.enableMultipage && pushHistory) {
      updateLocation(routerConfig, pageId);
    }
  };

  if (routerConfig.enableMultipage) {
    const initialEntry = await fetchManifestForPage(routerConfig, initialPageId);
    applyManifest(initialEntry);
    updateLocation(routerConfig, initialPageId, { replace: true });

    window.addEventListener(
      routerConfig.history === "hash" ? "hashchange" : "popstate",
      async () => {
        const target = currentPageFromLocation(routerConfig) ?? routerConfig.defaultPageId;
        await handleNavigate(target, false);
      },
    );

    window.addEventListener(NAV_EVENT, async (event: Event) => {
      const detail = (event as CustomEvent).detail || {};
      await handleNavigate(detail.pageId ?? null, true);
    });
  }

  if (config.clientSetup) {
    try {
      const setupFn = new Function("context", config.clientSetup);
      setupFn({
        config,
        manifest: app.manifest,
        registry: app.components,
      });
    } catch (error) {
      console.error("clientSetup execution failed", error);
    }
  }

  if (realtimeConfig.enabled && !app.mux) {
    const url = toWsUrl(realtimeConfig.path);
    if (url) {
      const socket = new WebSocket(url);
      socket.addEventListener("open", () => {
        if (realtimeConfig.autoSubscribe) {
          for (const channelId of realtimeConfig.channels ?? []) {
            socket.send(JSON.stringify({ action: "subscribe", channel: channelId }));
          }
        }
      });
      socket.addEventListener("message", (event) => {
        try {
          const data = JSON.parse(String(event.data));
          window.dispatchEvent(
            new CustomEvent(CHANNEL_EVENT, {
              detail: {
                channel: data.channel ?? null,
                payload: data.payload ?? null,
              },
            }),
          );
        } catch (error) {
          console.warn("Unable to parse realtime payload", error);
        }
      });
    }
  }

  return shell;
}

bootstrap().catch((error) => {
  console.error("Failed to bootstrap Svelte runtime", error);
});
