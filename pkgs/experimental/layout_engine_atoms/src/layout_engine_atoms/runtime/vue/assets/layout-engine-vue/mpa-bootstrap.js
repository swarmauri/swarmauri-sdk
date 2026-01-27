import {
  createApp,
  defineComponent,
  reactive,
  computed,
  watch,
  onMounted,
  onBeforeUnmount,
} from "vue";
import {
  createLayoutEnginePlugin,
  LayoutEngineShell,
  useSiteNavigation,
  loadManifest,
  WSMuxClient,
} from "./index.js";

const CONFIG_ELEMENT_ID = "le-shell-config";
const DEFAULT_TITLE = "Layout Engine Dashboard";
const DEFAULT_HEADER_TEMPLATE = `
  <header class="le-shell__header">
    <h1 class="le-shell__title">{{ shellTitle }}</h1>
    <p v-if="shellSubtitle" class="le-shell__subtitle">{{ shellSubtitle }}</p>
  </header>
`;
const DEFAULT_CONTENT_TEMPLATE = `
  <LayoutEngineShell>
    <template #default="{ site }">
      <nav v-if="site.pages.value.length" class="le-shell__nav">
        <button
          v-for="page in site.pages.value"
          :key="page.id"
          type="button"
          class="le-shell__nav-item"
          :class="{ 'is-active': page.id === site.activePage.value?.id }"
          @click="handleNavigate(page.id)"
        >
          <span class="le-shell__nav-label">{{ page.title ?? page.id }}</span>
          <span v-if="page.meta?.tagline" class="le-shell__nav-hint">{{ page.meta.tagline }}</span>
        </button>
      </nav>
    </template>
  </LayoutEngineShell>
`;

function parseShellConfig() {
  const el = document.getElementById(CONFIG_ELEMENT_ID);
  if (!el) return {};
  try {
    return JSON.parse(el.textContent || "{}");
  } catch (error) {
    console.error("Failed to parse shell configuration", error);
    return {};
  }
}

const REALTIME_EVENT = "layout-engine:channel";

const shellConfig = parseShellConfig();
const routerConfig = {
  manifestUrl: shellConfig.router?.manifestUrl ?? "./manifest.json",
  pageParam: shellConfig.router?.pageParam ?? "page",
  defaultPageId: shellConfig.router?.defaultPageId ?? null,
  history: shellConfig.router?.history ?? "history",
  hydrateThemeFromManifest:
    shellConfig.router?.hydrateThemeFromManifest ?? true,
  enableMultipage: shellConfig.router?.enableMultipage ?? false,
};

const realtimeConfig = normalizeRealtimeConfig(shellConfig.realtime);
const eventsConfig = normalizeEventsConfig(shellConfig.events);

const basePalette = shellConfig.theme?.accentPalette ?? {};

function normalizeRealtimeConfig(raw) {
  if (!raw || typeof raw !== "object") {
    return { enabled: false, channels: [] };
  }
  return {
    enabled: Boolean(raw.enabled && raw.path),
    path: raw.path ?? "",
    autoSubscribe: raw.autoSubscribe ?? true,
    channels: Array.isArray(raw.channels) ? raw.channels : [],
  };
}

function normalizeEventsConfig(raw) {
  if (!raw || typeof raw !== "object") {
    return { enabled: false, baseUrl: "", items: [] };
  }
  const baseUrl = typeof raw.baseUrl === "string" ? raw.baseUrl : "";
  const items = Array.isArray(raw.items) ? raw.items.filter((entry) => entry && typeof entry.id === "string") : [];
  return {
    enabled: Boolean(raw.enabled && baseUrl),
    baseUrl,
    items,
  };
}

function applyPalette(palette) {
  const root = document.documentElement;
  Object.entries(palette).forEach(([key, value]) => {
    root.style.setProperty(`--le-${key.replace(/_/g, "-")}`, value);
  });
}

applyPalette(basePalette);

function mergeThemeFromManifest(manifest) {
  if (!routerConfig.hydrateThemeFromManifest) {
    return;
  }
  const theme = manifest?.meta?.theme;
  if (!theme || typeof theme !== "object") {
    return;
  }
  applyPalette({ ...basePalette, ...theme });
}

function withPageParam(url, pageId) {
  if (!routerConfig.pageParam) {
    return url;
  }
  const [base, query = ""] = url.split("?");
  const params = new URLSearchParams(query);
  if (pageId) {
    params.set(routerConfig.pageParam, pageId);
  } else {
    params.delete(routerConfig.pageParam);
  }
  const queryString = params.toString();
  return queryString ? `${base}?${queryString}` : base;
}

function currentPageFromLocation() {
  if (!routerConfig.enableMultipage) {
    return null;
  }
  if (routerConfig.history === "hash") {
    const hash = window.location.hash.replace(/^#/, "");
    return hash || null;
  }
  const params = new URLSearchParams(window.location.search);
  return params.get(routerConfig.pageParam) || null;
}

function updateLocation(pageId, { replace = false } = {}) {
  if (!routerConfig.enableMultipage) {
    return;
  }

  if (routerConfig.history === "hash") {
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
    url.searchParams.set(routerConfig.pageParam, pageId);
  } else {
    url.searchParams.delete(routerConfig.pageParam);
  }
  if (replace) {
    window.history.replaceState({ pageId }, "", url);
  } else {
    window.history.pushState({ pageId }, "", url);
  }
}

const manifestCache = new Map();

function cloneManifestEntry(entry) {
  const manifestClone =
    typeof structuredClone === "function"
      ? structuredClone(entry.manifest)
      : JSON.parse(JSON.stringify(entry.manifest));
  const componentsClone = new Map(entry.components);
  return { manifest: manifestClone, components: componentsClone };
}

async function fetchManifestForPage(pageId) {
  const cacheKey = pageId || "__default__";
  if (manifestCache.has(cacheKey)) {
    return cloneManifestEntry(manifestCache.get(cacheKey));
  }

  const url = withPageParam(routerConfig.manifestUrl, pageId);
  const result = await loadManifest(url);
  manifestCache.set(cacheKey, result);
  return cloneManifestEntry(result);
}

function replaceManifest(target, source) {
  for (const key of Object.keys(target)) {
    if (!(key in source)) {
      delete target[key];
    }
  }
  for (const [key, value] of Object.entries(source)) {
    target[key] = value;
  }
}

function updateRegistry(target, source) {
  target.clear();
  source.forEach((entry, key) => {
    target.set(key, entry);
  });
}

function resolveWsUrl(path) {
  if (!path) {
    return null;
  }
  if (path.startsWith("ws://") || path.startsWith("wss://")) {
    return path;
  }
  const scheme = window.location.protocol === "https:" ? "wss" : "ws";
  const suffix = path.startsWith("/") ? path : `/${path}`;
  return `${scheme}://${window.location.host}${suffix}`;
}

function dispatchRealtimeEvent(channel, payload) {
  window.dispatchEvent(
    new CustomEvent(REALTIME_EVENT, {
      detail: {
        channel: channel ?? null,
        payload: payload ?? null,
      },
    }),
  );
}

function createRealtimeMuxBridge(config) {
  if (!config?.enabled) {
    return { mux: null, teardown: null };
  }
  const url = resolveWsUrl(config.path);
  if (!url) {
    return { mux: null, teardown: null };
  }
  const client = new WSMuxClient({ url });
  client.connect();
  window.__leRealtime = client;
  const subscriptions = [];
  if (config.autoSubscribe && Array.isArray(config.channels)) {
    for (const channelId of config.channels) {
      const unsubscribe = client.subscribe(channelId, (message) => {
        dispatchRealtimeEvent(message.channel ?? channelId, message.payload);
      });
      subscriptions.push(unsubscribe);
    }
  } else {
    client.on("message", (message) => {
      dispatchRealtimeEvent(message.channel, message.payload);
    });
  }
  client.on("error", (error) => {
    console.error("Realtime mux error", error);
  });
  const teardown = () => {
    subscriptions.forEach((unsubscribe) => {
      try {
        unsubscribe();
      } catch {
        /* noop */
      }
    });
    client.disconnect();
  };
  return {
    mux: { client, channels: config.channels ?? [] },
    teardown,
  };
}

function createEventsContext(config) {
  if (!config?.enabled || !config.baseUrl) {
    return null;
  }
  const normalizedBase = config.baseUrl.endsWith("/")
    ? config.baseUrl.slice(0, -1)
    : config.baseUrl;
  const descriptors = new Map();
  for (const entry of config.items ?? []) {
    descriptors.set(entry.id, entry);
  }
  const buildUrl = (eventId) => `${normalizedBase}/${encodeURIComponent(eventId)}`;
  const invoke = async (eventId, options = {}) => {
    if (!eventId) {
      throw new Error("Event id is required");
    }
    const descriptor = descriptors.get(eventId);
    const method = (options.method ?? descriptor?.method ?? "POST").toUpperCase();
    const payload = { ...(options.payload ?? {}) };
    if (options.context) {
      const existingContext = typeof payload.context === "object" ? payload.context : {};
      payload.context = { ...existingContext, ...options.context };
    }
    let target = buildUrl(eventId);
    const fetchOptions = {
      method,
      headers: { ...(options.headers ?? {}) },
    };
    if (method === "GET") {
      const url = new URL(target, window.location.origin);
      Object.entries(payload).forEach(([key, value]) => {
        if (value === undefined || value === null) return;
        url.searchParams.set(
          key,
          typeof value === "object" ? JSON.stringify(value) : String(value),
        );
      });
      target = `${url.pathname}${url.search}`;
    } else {
      fetchOptions.headers["content-type"] = "application/json";
      fetchOptions.body = JSON.stringify(payload);
    }
    const response = await fetch(target, fetchOptions);
    let body = null;
    try {
      body = await response.json();
    } catch {
      body = null;
    }
    if (!response.ok) {
      const error = new Error(body?.detail ?? "Event request failed");
      error.status = response.status;
      error.body = body;
      throw error;
    }
    const resolvedChannel =
      body?.channel ?? descriptor?.defaultChannel ?? null;
    const resolvedPayload =
      body?.payload ?? (typeof body === "object" ? body : null);
    if (resolvedChannel && resolvedPayload) {
      dispatchRealtimeEvent(resolvedChannel, resolvedPayload);
    }
    return { status: response.status, body };
  };
  return {
    enabled: true,
    invoke,
    describe: (eventId) => descriptors.get(eventId) ?? null,
  };
}

const initialPageId = currentPageFromLocation() || routerConfig.defaultPageId;
const initialManifestData = await fetchManifestForPage(initialPageId);

mergeThemeFromManifest(initialManifestData.manifest);

const manifestState = reactive(initialManifestData.manifest);
const registryState = new Map(initialManifestData.components);

const { mux: muxContext, teardown: teardownRealtime } =
  createRealtimeMuxBridge(realtimeConfig);
const eventsContext = createEventsContext(eventsConfig);
window.__leEvents = eventsContext;
const layoutPlugin = createLayoutEnginePlugin(manifestState, registryState, {
  mux: muxContext,
  events: eventsContext,
});
if (teardownRealtime) {
  window.addEventListener("beforeunload", () => teardownRealtime());
}

if (shellConfig.clientSetup) {
  try {
    // eslint-disable-next-line no-new-func
    const setupFn = new Function(
      "context",
      shellConfig.clientSetup
    );
    setupFn({
      config: shellConfig,
      manifest: manifestState,
      registry: registryState,
    });
  } catch (error) {
    console.error("clientSetup execution failed", error);
  }
}

function createHeaderComponent(template, context) {
  if (!template) return null;
  return defineComponent({
    name: "ShellHeader",
    setup: context,
    template,
  });
}

function createFooterComponent(template, context) {
  if (!template) return null;
  return defineComponent({
    name: "ShellFooter",
    setup: context,
    template,
  });
}

function createContentComponent(template, context) {
  return defineComponent({
    name: "ShellContent",
    components: { LayoutEngineShell },
    setup: context,
    template,
  });
}

const ShellApp = defineComponent({
  name: "LayoutEngineShellApp",
  components: {
    LayoutEngineShell,
  },
  setup() {
    const site = useSiteNavigation(manifestState);
    const status = reactive({
      isLoading: false,
      error: null,
    });

    const shellTitle = computed(
      () =>
        manifestState.meta?.page?.title ??
        shellConfig.title ??
        DEFAULT_TITLE
    );
    const shellSubtitle = computed(
      () => manifestState.meta?.page?.description ?? manifestState.meta?.page?.tagline ?? ""
    );

    const headerTemplate =
      shellConfig.ui?.headerSlot ?? DEFAULT_HEADER_TEMPLATE;
    const footerTemplate = shellConfig.ui?.footerSlot ?? "";
    const navTemplate = shellConfig.ui?.navSlot ?? null;
    const contentTemplate =
      shellConfig.ui?.contentSlot ??
      (navTemplate
        ? `<LayoutEngineShell>
            <template #default="{ site }">
              ${navTemplate}
            </template>
          </LayoutEngineShell>`
        : DEFAULT_CONTENT_TEMPLATE);

    const headerComponent = createHeaderComponent(headerTemplate, () => ({
      shellTitle,
      shellSubtitle,
    }));
    const footerComponent = createFooterComponent(footerTemplate, () => ({}));

    let suppressHashChange = false;

    const handleNavigate = async (pageId, { pushHistory = true } = {}) => {
      if (!pageId) return;
      if (!routerConfig.enableMultipage) {
        site.navigate(pageId);
        if (pushHistory) {
          updateLocation(pageId);
        }
        return;
      }
      status.isLoading = true;
      try {
        const { manifest, components } = await fetchManifestForPage(pageId);
        replaceManifest(manifestState, manifest);
        updateRegistry(registryState, components);
        site.navigate(pageId);
        mergeThemeFromManifest(manifest);
        if (pushHistory) {
          if (routerConfig.history === "hash") {
            suppressHashChange = true;
          }
          updateLocation(pageId);
        }
        status.error = null;
      } catch (error) {
        console.error("Failed to load manifest for page", pageId, error);
        status.error = "Failed to load dashboard page.";
      } finally {
        status.isLoading = false;
      }
    };

    const contentComponent = createContentComponent(contentTemplate, () => ({
      site,
      manifest: manifestState,
      handleNavigate,
    }));

    watch(
      () => manifestState.meta,
      () => mergeThemeFromManifest(manifestState),
      { deep: true, immediate: true }
    );

    if (routerConfig.enableMultipage) {
      const handler = async () => {
        if (routerConfig.history === "hash" && suppressHashChange) {
          suppressHashChange = false;
          return;
        }
        const target = currentPageFromLocation() || routerConfig.defaultPageId;
        if (target) {
          await handleNavigate(target, { pushHistory: false });
        }
      };
      if (routerConfig.history === "hash") {
        window.addEventListener("hashchange", handler);
      } else {
        window.addEventListener("popstate", handler);
      }
      onBeforeUnmount(() => {
        if (routerConfig.history === "hash") {
          window.removeEventListener("hashchange", handler);
        } else {
          window.removeEventListener("popstate", handler);
        }
      });
    }

    onMounted(() => {
      if (routerConfig.enableMultipage) {
        const initial = currentPageFromLocation() || routerConfig.defaultPageId;
        if (initial) {
          updateLocation(initial, { replace: true });
        }
      }
    });

    return {
      headerComponent,
      contentComponent,
      footerComponent,
      status,
    };
  },
  template: `
    <div class="le-shell-app">
      <component v-if="headerComponent" :is="headerComponent" />
      <section class="le-shell-app__body">
        <component :is="contentComponent" />
      </section>
      <component v-if="footerComponent" :is="footerComponent" />
      <div v-if="status.isLoading" class="le-shell__loading">Loading…</div>
      <div v-if="status.error" class="le-shell__error">{{ status.error }}</div>
    </div>
  `,
});

const app = createApp(ShellApp);
app.use(layoutPlugin);

const mountEl = document.getElementById("le-app");
if (!mountEl) {
  throw new Error("Unable to find mount element '#le-app'");
}
app.mount(mountEl);
