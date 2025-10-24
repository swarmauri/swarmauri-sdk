<script>
  import { onMount, onDestroy, setContext } from "svelte";
  import { derived, writable, get } from "svelte/store";
  import TileHost from "./TileHost.svelte";
  import { LAYOUT_CONTEXT_KEY } from "../context.js";
  import {
    createRuntimeState,
    createThemeController,
    mergeTheme,
    manifestFromPayload,
    createEventBridge,
    deriveEventsUrl,
    isPlainObject,
    createDocumentThemeApplier,
  } from "../../core/index.js";

  export let runtime;
  export let manifestUrl = "";
  export let fetchOptions = {};
  export let components = {};
  export let plugins = null;
  export let theme = {};
  export let initialPageId = null;
  export let pageId = null;
  export let resolvePage = null;
  export let onError = null;
  export let onReady = null;
  export let onPageChange = null;
  export let events = null;

  const runtimeState = createRuntimeState({
    manifestUrl: manifestUrl ?? null,
    initialPageId: pageId ?? initialPageId ?? null,
    resolvePage,
    initiallyLoading: true,
  });

  const stateStore = writable({
    manifest: runtimeState.state.manifest,
    loading: runtimeState.state.loading,
    error: runtimeState.state.error,
    pageId: runtimeState.state.pageId,
    view: runtimeState.state.view,
  });

  const unsubscribeRuntime = runtimeState.subscribe((next) => {
    stateStore.set({
      manifest: next.manifest,
      loading: next.loading,
      error: next.error,
      pageId: next.pageId,
      view: next.view,
    });
  });

  const state = stateStore;
  const view = derived(stateStore, ($state) => $state.view);
  const summary = derived(stateStore, ($state) => {
    const tiles = $state.view?.tiles ?? [];
    const roles = new Set(tiles.map((tile) => tile.role));
    return {
      tileCount: tiles.length,
      roleCount: roles.size,
    };
  });

  const themeController = createThemeController(runtime?.defaultTheme ?? {});

  function snapshotTheme() {
    return {
      className: themeController.state.className,
      style: { ...themeController.state.style },
      tokens: { ...themeController.state.tokens },
    };
  }

  const themeStore = writable(snapshotTheme());

  function syncThemeStore() {
    themeStore.set(snapshotTheme());
  }

  function applyTheme(patch, options = {}) {
    if (options?.replace) {
      themeController.reset(runtime?.defaultTheme ?? {});
    }
    if (patch) {
      themeController.apply(patch);
    }
    syncThemeStore();
  }

  const runtimeTheme = derived(
    [themeStore, view],
    ([$theme, $view]) => mergeTheme($theme, $view?.page?.theme),
  );

  const rootClass = derived(runtimeTheme, ($theme) => {
    const classes = ["dashboard"];
    if ($theme?.className) {
      $theme.className
        .split(/\s+/)
        .filter(Boolean)
        .forEach((token) => classes.push(token));
    }
    return classes.join(" ");
  });

  function styleObjectToString(style) {
    if (!style) {
      return "";
    }
    return Object.entries(style)
      .filter(([, value]) => value !== undefined && value !== null)
      .map(([key, value]) => {
        const kebab = key.replace(/([A-Z])/g, "-$1").toLowerCase();
        return `${kebab}: ${value}`;
      })
      .join("; ");
  }

  const rootStyle = derived(runtimeTheme, ($theme) => {
    const style = { ...($theme?.style ?? {}) };
    const tokens = $theme?.tokens ?? {};
    for (const [token, value] of Object.entries(tokens)) {
      style[`--le-${token}`] = value;
    }
    return style;
  });

  const rootStyleString = derived(rootStyle, (style) => styleObjectToString(style));

  const gridStyle = derived(view, ($view) => {
    const grid = $view?.grid ?? null;
    if (!grid) {
      return {};
    }
    const columnCount = grid.columns?.length ?? 1;
    return {
      gridTemplateColumns: `repeat(${columnCount}, minmax(200px, 1fr))`,
      gap: `${grid.gap_y ?? 0}px ${grid.gap_x ?? 0}px`,
    };
  });

  const gridStyleString = derived(gridStyle, (style) => styleObjectToString(style));

  const dashboardTitle = derived([view, state], ([$view, $state]) => {
    const page = $view?.page ?? null;
    if (page?.label) {
      return page.label;
    }
    if (page?.title) {
      return page.title;
    }
    const manifest = $state.manifest ?? null;
    if (manifest?.title) {
      return manifest.title;
    }
    if (manifest?.label) {
      return manifest.label;
    }
    return "Dashboard";
  });

  const eventsState = writable({
    enabled: false,
    status: "idle",
    url: null,
    connected: false,
    attempts: 0,
    lastError: null,
  });

  let mergedComponents = combineComponents(runtime?.baseRenderers ?? {}, components);
  $: mergedComponents = combineComponents(runtime?.baseRenderers ?? {}, components);

  function combineComponents(base, custom) {
    const overrides = custom ?? {};
    const combined = { ...base, ...overrides };
    if (!combined.default && base?.default) {
      combined.default = base.default;
    }
    return combined;
  }

  let mounted = false;
  let lastResolvedManifestUrl = null;
  let lastPageIdProp = pageId;
  let lastThemeProp = theme;
  let eventBridge = null;
  let bridgeSubscriptions = [];
  let lastEventsConfig = null;

  const applyDocumentTheme = createDocumentThemeApplier();
  const runtimeThemeUnsub = runtimeTheme.subscribe((next) => {
    applyDocumentTheme(next);
  });

  function resolveGlobalManifestUrl() {
    if (manifestUrl) {
      return manifestUrl;
    }
    if (typeof window !== "undefined" && window) {
      return (
        window.__LE_MANIFEST_URL__ ??
        new URL("manifest.json", window.location.href).toString()
      );
    }
    return "manifest.json";
  }

  $: resolvedManifestUrl = resolveGlobalManifestUrl();

  function resolveGlobalEventsOptions() {
    if (typeof window === "undefined") {
      return null;
    }
    if (!window.__LE_EVENTS_ENABLED__) {
      return null;
    }
    const globalOptions = window.__LE_EVENTS_OPTIONS__;
    if (isPlainObject(globalOptions)) {
      return { ...globalOptions };
    }
    const url = window.__LE_EVENTS_URL__;
    if (typeof url === "string" && url) {
      return { url };
    }
    return {};
  }

  function toEventsOptions(raw) {
    if (raw === undefined || raw === null) {
      return resolveGlobalEventsOptions();
    }
    if (raw === false) {
      return null;
    }
    if (raw === true) {
      return {};
    }
    if (typeof raw === "string") {
      return { url: raw };
    }
    if (isPlainObject(raw)) {
      return { ...raw };
    }
    return null;
  }

  $: eventsOptions = toEventsOptions(events);

  $: {
    const baseFetchOptions = fetchOptions ?? {};
    runtimeState.setFetcher(async (url, overrideOptions) => {
      const response = await fetch(url, {
        ...baseFetchOptions,
        ...(overrideOptions ?? {}),
      });
      return response;
    });
  }

  function recordEventError(message) {
    eventsState.update((state) => ({ ...state, lastError: message }));
  }

  function resetEventsState() {
    eventsState.set({
      enabled: false,
      status: "idle",
      url: null,
      connected: false,
      attempts: 0,
      lastError: null,
    });
  }

  function teardownBridge() {
    bridgeSubscriptions.forEach((unsubscribe) => {
      try {
        unsubscribe?.();
      } catch {
        // ignore cleanup errors
      }
    });
    bridgeSubscriptions = [];
    if (eventBridge) {
      eventBridge.close();
      eventBridge = null;
    }
    resetEventsState();
  }

  function ensureBridge(options) {
    if (eventBridge) {
      return eventBridge;
    }
    const reconnect =
      options?.autoReconnect === undefined
        ? true
        : Boolean(options.autoReconnect);
    eventBridge = createEventBridge({
      autoConnect: false,
      autoReconnect: reconnect,
      reconnectDelay: options?.reconnectDelay ?? 2000,
      protocols: options?.protocols,
      windowRef: typeof window !== "undefined" ? window : null,
    });
    bridgeSubscriptions.push(
      eventBridge.on("status", (detail) => {
        if (!detail) {
          return;
        }
        eventsState.update((state) => {
          const next = { ...state };
          if (detail.type === "connecting") {
            next.status = "connecting";
            next.connected = false;
            next.attempts =
              typeof detail.attempts === "number"
                ? detail.attempts
                : state.attempts + 1;
          } else if (detail.type === "open") {
            next.status = "open";
            next.connected = true;
            next.attempts = 0;
          } else if (detail.type === "closed") {
            next.status = "closed";
            next.connected = false;
          } else if (detail.type === "url") {
            next.url = detail.url ?? state.url;
          }
          return next;
        });
      }),
      eventBridge.on("open", () => {
        eventsState.update((state) => ({
          ...state,
          status: "open",
          connected: true,
          lastError: null,
        }));
      }),
      eventBridge.on("close", () => {
        eventsState.update((state) => ({
          ...state,
          connected: false,
        }));
      }),
      eventBridge.on("error", (event) => {
        eventsState.update((state) => ({
          ...state,
          status: "error",
          connected: false,
        }));
        recordEventError(
          event instanceof Error
            ? event.message
            : event?.message ?? "WebSocket error",
        );
      }),
      eventBridge.on("message", handleBridgeMessage),
    );
    return eventBridge;
  }

  function handleBridgeMessage(event) {
    const raw = event?.data ?? event;
    if (raw === undefined || raw === null) {
      return;
    }

    let payload = null;
    if (typeof raw === "string") {
      try {
        payload = JSON.parse(raw);
      } catch {
        return;
      }
    } else if (raw instanceof ArrayBuffer) {
      try {
        const text = new TextDecoder("utf-8").decode(raw);
        payload = JSON.parse(text);
      } catch {
        return;
      }
    } else if (raw?.text && typeof raw.text === "function") {
      raw
        .text()
        .then((text) => {
          try {
            handleBridgeMessage({ data: JSON.parse(text) });
          } catch {
            // ignore invalid JSON payloads
          }
        })
        .catch(() => {
          /* ignore blob read errors */
        });
      return;
    } else if (typeof raw === "object") {
      payload = raw;
    }

    if (!payload || typeof payload !== "object") {
      return;
    }

    const opts = eventsOptions ?? {};
    const topic = payload.topic ?? null;
    const body = payload.payload ?? payload;
    const manifestTopic = opts.topic ?? "manifest";
    let handled = false;

    const manifest = manifestFromPayload(body);
    if (manifest && (!topic || topic === manifestTopic)) {
      runtimeState.setManifest(manifest);
      opts.onManifest?.(manifest);
      handled = true;
    } else {
      const eventType = body?.type ?? payload?.type ?? null;
      if (eventType === "manifest.refresh") {
        fetchManifest();
        handled = true;
      } else if (eventType === "manifest.patch" && isPlainObject(body?.patch)) {
        const merged = runtimeState.applyPatch(body.patch);
        opts.onManifest?.(merged ?? runtimeState.state.manifest);
        handled = true;
      } else if (eventType === "manifest.replace" && manifest) {
        runtimeState.setManifest(manifest);
        opts.onManifest?.(manifest);
        handled = true;
      }
    }

    if (handled) {
      recordEventError(null);
    } else if (typeof opts.onMessage === "function") {
      try {
        opts.onMessage(payload, { topic, payload: body });
      } catch (error) {
        console.error("[layout-engine-svelte] events.onMessage error", error);
      }
    }
  }

  function sendRuntimeEvent(message) {
    if (!eventBridge) {
      recordEventError("WebSocket not connected");
      return false;
    }
    let payload = message;
    if (
      typeof payload !== "string" &&
      !(payload instanceof ArrayBuffer) &&
      !ArrayBuffer.isView(payload)
    ) {
      try {
        payload = JSON.stringify(payload);
      } catch (error) {
        recordEventError(
          error instanceof Error ? error.message : String(error),
        );
        return false;
      }
    }
    const sent = eventBridge.send(payload);
    if (!sent) {
      recordEventError("WebSocket not open");
    }
    return sent;
  }

  function runtimeReconnectEvents() {
    eventBridge?.connect();
  }

  function runtimeDisconnectEvents() {
    eventBridge?.close();
  }

  function configureEvents(manifestUrlValue, options) {
    if (!options || options.enabled === false) {
      eventsState.update((state) => ({
        ...state,
        enabled: false,
        url: null,
        status: options?.enabled === false ? "disabled" : "idle",
      }));
      teardownBridge();
      return;
    }
    if (typeof window === "undefined") {
      eventsState.update((state) => ({
        ...state,
        enabled: false,
        url: null,
        status: "unavailable",
      }));
      return;
    }
    if (!manifestUrlValue) {
      eventsState.update((state) => ({
        ...state,
        enabled: false,
        url: null,
      }));
      teardownBridge();
      return;
    }

    const derivedUrl = deriveEventsUrl({
      manifestUrl: manifestUrlValue,
      explicitUrl: options.url ?? options.eventsUrl ?? null,
      windowRef: window,
    });
    if (!derivedUrl) {
      eventsState.update((state) => ({
        ...state,
        enabled: false,
        url: null,
      }));
      teardownBridge();
      return;
    }

    eventsState.update((state) => ({
      ...state,
      enabled: true,
      url: derivedUrl,
    }));
    const bridge = ensureBridge(options);
    bridge.setUrl(derivedUrl);
    bridge.connect();
  }

  function eventsConfigSignature(manifestUrlValue, options) {
    if (!options) {
      return `none::${manifestUrlValue ?? "null"}`;
    }
    const clean = { ...options };
    delete clean.onManifest;
    delete clean.onMessage;
    let encoded = "";
    try {
      encoded = JSON.stringify(clean);
    } catch {
      encoded = "[unserializable]";
    }
    return `${manifestUrlValue ?? "null"}::${encoded}`;
  }

  $: {
    const signature = eventsConfigSignature(resolvedManifestUrl, eventsOptions);
    if (mounted && signature !== lastEventsConfig) {
      lastEventsConfig = signature;
      configureEvents(resolvedManifestUrl, eventsOptions);
    }
  }

  $: if (resolvePage !== undefined) {
    runtimeState.setResolvePage(resolvePage);
  }

  $: {
    const nextTheme = theme ?? null;
    if (nextTheme !== lastThemeProp) {
      lastThemeProp = nextTheme;
      if (nextTheme) {
        applyTheme(nextTheme, { replace: true });
      } else {
        themeController.reset(runtime?.defaultTheme ?? {});
        syncThemeStore();
      }
    }
  }

  function emitPageChange(page) {
    const key = page?.id ?? page?.slug ?? page?.name ?? null;
    if (key === emitPageChange.lastKey && page === emitPageChange.lastRef) {
      return;
    }
    emitPageChange.lastKey = key;
    emitPageChange.lastRef = page ?? null;
    onPageChange?.(key, page ?? null);
  }
  emitPageChange.lastKey = null;
  emitPageChange.lastRef = null;

  function runtimeSetPage(nextPageId) {
    const page = runtimeState.setPage(nextPageId);
    emitPageChange(page ?? runtimeState.state.view.page);
    return page;
  }

  const viewUnsub = view.subscribe(($view) => {
    emitPageChange($view?.page ?? null);
  });

  $: if (pageId !== undefined && pageId !== null) {
    if (pageId !== lastPageIdProp) {
      lastPageIdProp = pageId;
      runtimeSetPage(pageId);
    }
  } else {
    lastPageIdProp = pageId;
  }

  $: {
    const nextInitial = initialPageId;
    if (nextInitial !== undefined && nextInitial !== null) {
      const currentView = get(view);
      if (!currentView?.page) {
        runtimeSetPage(nextInitial);
      }
    }
  }

  async function fetchManifest(url = resolvedManifestUrl) {
    if (!url) {
      runtimeState.setManifestUrl(null);
      runtimeState.setLoading(false);
      return null;
    }
    runtimeState.setManifestUrl(url);
    try {
      const manifest = await runtimeState.fetchManifest(url);
      onReady?.(manifest);
      return manifest;
    } catch (error) {
      const err = error instanceof Error ? error : new Error(String(error));
      console.error("[layout-engine-svelte] fetchManifest failed", err);
      onError?.(err);
      return null;
    }
  }

  $: if (resolvedManifestUrl !== lastResolvedManifestUrl) {
    lastResolvedManifestUrl = resolvedManifestUrl;
    runtimeState.setManifestUrl(resolvedManifestUrl ?? null);
    if (mounted) {
      if (resolvedManifestUrl) {
        fetchManifest(resolvedManifestUrl);
      } else {
        runtimeState.setLoading(false);
      }
    }
  }

  const pluginManager = plugins?.manager ?? null;
  const pluginContext = {
    get state() {
      return get(stateStore);
    },
    get view() {
      return get(view);
    },
    get events() {
      return get(eventsState);
    },
    refresh: () => fetchManifest(resolvedManifestUrl),
    setPage: runtimeSetPage,
    setTheme: applyTheme,
    sendEvent: sendRuntimeEvent,
  };

  pluginManager?.runHook("beforeRender", pluginContext);

  const pluginUpdateUnsub = derived(
    [stateStore, view, eventsState],
    () => ({})
  ).subscribe(() => {
    pluginManager?.runHook("afterUpdate", pluginContext);
  });

  onMount(() => {
    mounted = true;
    if (resolvedManifestUrl) {
      fetchManifest(resolvedManifestUrl);
    } else {
      runtimeState.setLoading(false);
    }
  });

  onDestroy(() => {
    mounted = false;
    teardownBridge();
    unsubscribeRuntime();
    runtimeThemeUnsub();
    viewUnsub();
    pluginUpdateUnsub();
  });

  const layoutContext = {
    setPage: runtimeSetPage,
    sendEvent: sendRuntimeEvent,
    refresh: () => fetchManifest(resolvedManifestUrl),
  };
  setContext(LAYOUT_CONTEXT_KEY, layoutContext);

  export function refresh() {
    return fetchManifest(resolvedManifestUrl);
  }

  export function setPage(nextPageId) {
    return runtimeSetPage(nextPageId);
  }

  export function setTheme(patch, options) {
    return applyTheme(patch, options);
  }

  export function getState() {
    return get(stateStore);
  }

  export function getRuntimeTheme() {
    return get(runtimeTheme);
  }

  export function sendEvent(message) {
    return sendRuntimeEvent(message);
  }

  export function reconnectEvents() {
    runtimeReconnectEvents();
  }

  export function disconnectEvents() {
    runtimeDisconnectEvents();
  }

  export function getEventsState() {
    return get(eventsState);
  }
</script>

<div class={$rootClass} style={$rootStyleString}>
  <header class="dashboard__header">
    <div>
      <h1 class="dashboard__title">{$dashboardTitle}</h1>
      <p class="dashboard__meta">
        <span>Manifest v{$state.manifest?.version ?? "—"}</span>
        <span aria-hidden="true">•</span>
        <span>Tiles: {$summary.tileCount}</span>
        <span aria-hidden="true">•</span>
        <span>Roles: {$summary.roleCount}</span>
      </p>
    </div>
    <div class="dashboard__meta">
      <span>
        Viewport:
        {$view.viewport?.width ?? $state.manifest?.viewport?.width ?? "—"}×
        {$view.viewport?.height ?? $state.manifest?.viewport?.height ?? "—"}
      </span>
      <span aria-hidden="true">•</span>
      <span>Generated by layout-engine</span>
    </div>
  </header>

  {#if $state.loading}
    <div class="dashboard__meta">Fetching manifest…</div>
  {:else if $state.error}
    <div class="dashboard__meta">
      Failed to load manifest: {$state.error.message}
    </div>
  {/if}

  {#if $state.manifest && !$state.error && $view.tiles.length}
    <section class="dashboard-grid" style={$gridStyleString}>
      {#each $view.tiles as tile (tile.id)}
        <TileHost
          {tile}
          grid={$view.grid}
          viewport={$view.viewport || $state.manifest?.viewport}
          components={mergedComponents}
          baseRenderers={runtime?.baseRenderers ?? {}}
        />
      {/each}
    </section>
  {:else if $state.manifest && !$state.error}
    <div class="dashboard__meta">No tiles available for the selected page.</div>
  {/if}
</div>
