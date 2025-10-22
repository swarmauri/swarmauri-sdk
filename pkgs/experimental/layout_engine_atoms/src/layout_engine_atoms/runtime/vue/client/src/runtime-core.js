import { createAtomRenderers } from "./atom-renderers.js";
import {
  createRuntimeState,
  createThemeController,
  mergeTheme,
  createPluginManager,
  manifestFromPayload,
  createEventBridge,
  deriveEventsUrl,
  isPlainObject,
  computeGridPlacement,
  createDocumentThemeApplier,
  SWISS_GRID_THEME,
} from "../core/index.js";


export function createRuntime(vue, options = {}) {
  const {
    computed,
    createApp,
    defineComponent,
    h,
    reactive,
    ref,
    watch,
    onBeforeUnmount,
    provide,
    inject,
  } = vue;
  if (
    !computed ||
    !createApp ||
    !defineComponent ||
    !h ||
    !reactive ||
    !ref ||
    !watch ||
    !onBeforeUnmount ||
    !provide ||
    !inject
  ) {
    throw new Error(
      "createRuntime requires Vue composition API exports including provide/inject",
    );
  }

  const defaultRenderers = createAtomRenderers({
    computed,
    defineComponent,
    h,
    inject,
  });
  const rendererOverrides = options.atomRenderers ?? {};
  const baseRenderers = {
    ...defaultRenderers,
    ...rendererOverrides,
  };
  if (!baseRenderers.default) {
    baseRenderers.default = defaultRenderers.default;
  }

  const defaultTheme = mergeTheme(SWISS_GRID_THEME, options.theme);
  const basePluginList = Array.isArray(options.plugins)
    ? options.plugins.filter(Boolean)
    : [];

  const TileHost = defineComponent({
    name: "LayoutEngineTileHost",
    props: {
      tile: { type: Object, required: true },
      grid: { type: Object, required: false, default: null },
      viewport: { type: Object, required: false, default: null },
      components: { type: Object, required: true },
    },
    setup(props) {
      const renderer = computed(() => {
        const registry = props.components ?? baseRenderers;
        return (
          registry[props.tile.role] ??
          registry.default ??
          baseRenderers.default
        );
      });

      const placement = computed(() =>
        computeGridPlacement(props.tile.frame, props.grid, props.viewport),
      );

      return {
        renderer,
        placement,
      };
    },
    template: `
      <div class="tile" :style="placement">
        <component :is="renderer" :tile="tile" />
      </div>
    `,
  });

  const DashboardApp = defineComponent({
    name: "LayoutEngineDashboard",
    components: { TileHost },
    props: {
      manifestUrl: { type: String, default: "" },
      fetchOptions: {
        type: Object,
        default: () => ({}),
      },
      components: {
        type: Object,
        default: () => ({}),
      },
      plugins: {
        type: Object,
        default: () => null,
      },
      theme: {
        type: Object,
        default: () => ({}),
      },
      initialPageId: {
        type: [String, Number],
        default: null,
      },
      pageId: {
        type: [String, Number],
        default: null,
      },
      resolvePage: {
        type: Function,
        default: null,
      },
      onError: {
        type: Function,
        default: null,
      },
      onReady: {
        type: Function,
        default: null,
      },
      onPageChange: {
        type: Function,
        default: null,
      },
      events: {
        type: [Boolean, String, Object],
        default: null,
      },
    },
    setup(props, { expose }) {
      const runtimeState = createRuntimeState({
        manifestUrl: props.manifestUrl ?? null,
        initialPageId: props.pageId ?? props.initialPageId ?? null,
        resolvePage: props.resolvePage,
        initiallyLoading: true,
      });

      runtimeState.setFetcher(async (url, overrideOptions) => {
        const response = await fetch(url, {
          ...(props.fetchOptions ?? {}),
          ...(overrideOptions ?? {}),
        });
        return response;
      });

      const state = reactive({
        manifest: runtimeState.state.manifest,
        loading: runtimeState.state.loading,
        error: runtimeState.state.error,
        pageId: runtimeState.state.pageId,
        view: runtimeState.state.view,
      });

      runtimeState.subscribe((next) => {
        state.manifest = next.manifest;
        state.loading = next.loading;
        state.error = next.error;
        state.pageId = next.pageId;
        state.view = next.view;
      });

      const themeController = createThemeController(defaultTheme);
      const themeState = reactive(themeController.state);

      function applyTheme(patch, options) {
        if (options?.replace) {
          themeController.reset(defaultTheme);
        }
        if (patch) {
          themeController.apply(patch);
        }
      }

      if (props.theme) {
        applyTheme(props.theme, { replace: true });
      }

      watch(
        () => props.theme,
        (next) => {
          applyTheme(next, { replace: true });
        },
        { deep: true }
      );

      watch(
        () => props.fetchOptions,
        () => {
          runtimeState.setFetcher(async (url, overrideOptions) => {
            const response = await fetch(url, {
              ...(props.fetchOptions ?? {}),
              ...(overrideOptions ?? {}),
            });
            return response;
          });
        },
        { deep: true }
      );

      const mergedComponents = computed(() => {
        const custom = props.components ?? {};
        const combined = { ...baseRenderers, ...custom };
        if (!combined.default && baseRenderers.default) {
          combined.default = baseRenderers.default;
        }
        return combined;
      });

      watch(
        () => props.resolvePage,
        (next) => {
          runtimeState.setResolvePage(next);
        },
      );

      const resolvedManifestUrl = computed(() => {
        if (props.manifestUrl) {
          return props.manifestUrl;
        }
        if (typeof window !== "undefined" && window) {
          return (
            window.__LE_MANIFEST_URL__ ??
            new URL("manifest.json", window.location.href).toString()
          );
        }
        return "manifest.json";
      });

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

      const eventsOptions = computed(() => {
        const raw = props.events;
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
      });

      const eventsState = reactive({
        enabled: false,
        status: "idle",
        url: null,
        connected: false,
        attempts: 0,
        lastError: null,
      });

      let eventBridge = null;
      const bridgeSubscriptions = [];

      function recordEventError(message) {
        eventsState.lastError = message;
      }

      function resetEventsState() {
        eventsState.status = "idle";
        eventsState.connected = false;
        eventsState.attempts = 0;
      }

      function teardownBridge() {
        while (bridgeSubscriptions.length) {
          const unsub = bridgeSubscriptions.pop();
          try {
            unsub?.();
          } catch {
            // ignore cleanup errors
          }
        }
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
            if (detail.type === "connecting") {
              eventsState.status = "connecting";
              eventsState.connected = false;
              eventsState.attempts =
                typeof detail.attempts === "number"
                  ? detail.attempts
                  : eventsState.attempts + 1;
            } else if (detail.type === "open") {
              eventsState.status = "open";
              eventsState.connected = true;
              eventsState.attempts = 0;
            } else if (detail.type === "closed") {
              eventsState.status = "closed";
              eventsState.connected = false;
            } else if (detail.type === "url") {
              eventsState.url = detail.url ?? eventsState.url;
            }
          }),
          eventBridge.on("open", () => {
            eventsState.status = "open";
            eventsState.connected = true;
            recordEventError(null);
          }),
          eventBridge.on("close", () => {
            eventsState.connected = false;
          }),
          eventBridge.on("error", (event) => {
            eventsState.status = "error";
            eventsState.connected = false;
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

        const opts = eventsOptions.value ?? {};
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
            console.error("[layout-engine-vue] events.onMessage error", error);
          }
        }
      }

      function sendEvent(message) {
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

      function reconnectEvents() {
        if (eventBridge) {
          eventBridge.connect();
        }
      }

      function disconnectEvents() {
        if (eventBridge) {
          eventBridge.close();
        }
      }

      watch(
        [resolvedManifestUrl, eventsOptions],
        ([manifestUrl, options]) => {
          if (!options) {
            eventsState.enabled = false;
            eventsState.url = null;
            teardownBridge();
            return;
          }
          if (options.enabled === false) {
            eventsState.enabled = false;
            eventsState.url = null;
            teardownBridge();
            return;
          }
          if (typeof window === "undefined") {
            eventsState.enabled = false;
            eventsState.url = null;
            return;
          }

          const derivedUrl = deriveEventsUrl({
            manifestUrl,
            explicitUrl: options.url ?? options.eventsUrl ?? null,
            windowRef: window,
          });
          if (!derivedUrl) {
            eventsState.enabled = false;
            eventsState.url = null;
            teardownBridge();
            return;
          }

          eventsState.enabled = true;
          eventsState.url = derivedUrl;
          const bridge = ensureBridge(options);
          bridge.setUrl(derivedUrl);
          bridge.connect();
        },
        { immediate: true },
      );

      onBeforeUnmount(() => {
        teardownBridge();
      });

      let lastEmittedPageKey = null;
      let lastEmittedPageRef = null;

      function emitPageChange(page) {
        const key = page?.id ?? page?.slug ?? page?.name ?? null;
        if (key === lastEmittedPageKey && page === lastEmittedPageRef) {
          return;
        }
        lastEmittedPageKey = key;
        lastEmittedPageRef = page ?? null;
        props.onPageChange?.(key, page ?? null);
      }

      const view = computed(() => state.view);

      async function fetchManifest(url = resolvedManifestUrl.value) {
        if (!url) {
          runtimeState.setManifestUrl(null);
          runtimeState.setLoading(false);
          return null;
        }
        runtimeState.setManifestUrl(url);
        try {
          const manifest = await runtimeState.fetchManifest(url);
          props.onReady?.(manifest);
          return manifest;
        } catch (error) {
          const err =
            error instanceof Error ? error : new Error(String(error));
          console.error("[layout-engine-vue] fetchManifest failed", err);
          props.onError?.(err);
          return null;
        }
      }

      function setPage(nextPageId) {
        const page = runtimeState.setPage(nextPageId);
        emitPageChange(page ?? runtimeState.state.view.page);
        return page;
      }

      watch(
        () => state.view.page,
        (page) => {
          emitPageChange(page);
        },
      );

      const gridStyle = computed(() => {
        const grid = view.value.grid;
        if (!grid) {
          return {};
        }
        const columnCount = grid.columns?.length ?? 1;
        return {
          gridTemplateColumns: `repeat(${columnCount}, minmax(200px, 1fr))`,
          gap: `${grid.gap_y}px ${grid.gap_x}px`,
        };
      });

      const summary = computed(() => {
        const tiles = view.value.tiles ?? [];
        const roles = new Set(tiles.map((tile) => tile.role));
        return {
          tileCount: tiles.length,
          roleCount: roles.size,
        };
      });

      const dashboardTitle = computed(() => {
        const page = view.value.page;
        if (page?.label) {
          return page.label;
        }
        if (page?.title) {
          return page.title;
        }
        const manifest = state.manifest;
        if (manifest?.title) {
          return manifest.title;
        }
        if (manifest?.label) {
          return manifest.label;
        }
        return "Dashboard";
      });

      const runtimeTheme = computed(() => mergeTheme(themeState, view.value.page?.theme));

      const applyDocumentTheme = createDocumentThemeApplier();

      watch(
        runtimeTheme,
        (next) => {
          applyDocumentTheme(next);
        },
        { immediate: true, deep: true },
      );

      provide("layout-engine-context", {
        setPage,
        sendEvent,
        refresh: fetchManifest,
      });

      const rootClass = computed(() => {
        const classes = ["dashboard"];
        if (runtimeTheme.value.className) {
          runtimeTheme.value.className
            .split(/\s+/)
            .filter(Boolean)
            .forEach((name) => classes.push(name));
        }
        return classes;
      });

      const rootStyle = computed(() => {
        const style = { ...(runtimeTheme.value.style ?? {}) };
        const tokens = runtimeTheme.value.tokens ?? {};
        for (const [token, value] of Object.entries(tokens)) {
          style[`--le-${token}`] = value;
        }
        return style;
      });

      watch(
        () => props.pageId,
        (next) => {
          if (next !== undefined && next !== null) {
            setPage(next);
          }
        },
      );

      watch(
        () => props.initialPageId,
        (next) => {
          if (!state.view.page && next !== undefined && next !== null) {
            setPage(next);
          }
        },
      );

      watch(
        resolvedManifestUrl,
        (url) => {
          runtimeState.setManifestUrl(url ?? null);
          if (url) {
            fetchManifest(url);
          }
        },
        { immediate: true },
      );

      function setTheme(patch, options) {
        applyTheme(patch, options);
      }

      const pluginManager = props.plugins?.manager ?? null;

      const pluginContext = {
        get state() {
          return state;
        },
        get view() {
          return view.value;
        },
        get events() {
          return eventsState;
        },
        refresh: fetchManifest,
        setPage,
        setTheme,
        sendEvent,
      };

      pluginManager?.runHook("beforeRender", pluginContext);

      watch(
        () => [state.manifest, view.value, eventsState.status],
        () => {
          pluginManager?.runHook("afterUpdate", pluginContext);
        },
        { flush: "post" },
      );

      expose({
        refresh: fetchManifest,
        state,
        setPage,
        setTheme,
        theme: themeState,
        events: {
          state: eventsState,
          send: sendEvent,
          reconnect: reconnectEvents,
          disconnect: disconnectEvents,
        },
      });

      return {
        state,
        view,
        gridStyle,
        summary,
        mergedComponents,
        rootClass,
        rootStyle,
        runtimeTheme,
        setPage,
        setTheme,
        eventsState,
        sendEvent,
        reconnectEvents,
        disconnectEvents,
        dashboardTitle,
      };
    },
    template: `
      <div :class="rootClass" :style="rootStyle">
        <header class="dashboard__header">
          <div>
            <h1 class="dashboard__title">{{ dashboardTitle }}</h1>
            <p class="dashboard__meta">
              <span>Manifest v{{ state.manifest?.version ?? "—" }}</span>
              <span aria-hidden="true">•</span>
              <span>Tiles: {{ summary.tileCount }}</span>
              <span aria-hidden="true">•</span>
              <span>Roles: {{ summary.roleCount }}</span>
            </p>
          </div>
          <div class="dashboard__meta">
            <span>
              Viewport: {{ view.viewport?.width ?? state.manifest?.viewport?.width ?? "—" }}×{{ view.viewport?.height ?? state.manifest?.viewport?.height ?? "—" }}
            </span>
            <span aria-hidden="true">•</span>
            <span>Generated by layout-engine</span>
          </div>
        </header>

        <div v-if="state.loading" class="dashboard__meta">Fetching manifest…</div>
        <div v-else-if="state.error" class="dashboard__meta">
          Failed to load manifest: {{ state.error.message }}
        </div>

        <section
          v-if="state.manifest && !state.error && view.tiles.length"
          class="dashboard-grid"
          :style="gridStyle"
        >
          <TileHost
            v-for="tile in view.tiles"
            :key="tile.id"
            :tile="tile"
            :grid="view.grid"
            :viewport="view.viewport || state.manifest?.viewport"
            :components="mergedComponents"
          />
        </section>

        <div v-else-if="state.manifest && !state.error" class="dashboard__meta">
          No tiles available for the selected page.
        </div>
      </div>
    `,
  });

  function createLayoutApp(userOptions = {}) {
    const targetSelector = userOptions.target ?? "#app";
    const manifestUrl = userOptions.manifestUrl ?? "";
    const componentsOverride = userOptions.components ?? {};
    const fetchOptions = userOptions.fetchOptions ?? {};
    const onError = userOptions.onError ?? null;
    const onReady = userOptions.onReady ?? null;
    const onPageChange = userOptions.onPageChange ?? null;
    const resolvePage = userOptions.resolvePage ?? options.pageResolver ?? null;
    const initialPageId = userOptions.initialPageId ?? null;
    const controlledPageId = userOptions.pageId ?? null;
    const themeOption = userOptions.theme ?? null;
    const eventsOption = userOptions.events ?? null;
    const runtimePlugins = Array.isArray(userOptions.plugins)
      ? userOptions.plugins.filter(Boolean)
      : [];

    const registeredComponents = reactive({ ...componentsOverride });
    const pluginManager = createPluginManager(basePluginList);
    runtimePlugins.forEach((plugin) => pluginManager.register(plugin));

    const props = {
      manifestUrl,
      fetchOptions,
      components: registeredComponents,
      plugins: { manager: pluginManager },
      theme: themeOption,
      initialPageId,
      pageId: controlledPageId,
      resolvePage,
      onError,
      onReady,
      onPageChange,
      events: eventsOption,
    };

    const app = createApp(DashboardApp, props);

    const mountTarget =
      typeof targetSelector === "string"
        ? typeof document !== "undefined"
          ? document.querySelector(targetSelector)
          : null
        : targetSelector;

    if (!mountTarget) {
      throw new Error(
        `Unable to find mount target "${targetSelector}". Ensure the element exists.`,
      );
    }

    const vm = app.mount(mountTarget);

    function registerAtomRenderer(role, component) {
      if (typeof role !== "string" || !role) {
        return;
      }
      if (component === undefined || component === null) {
        delete registeredComponents[role];
        return;
      }
      registeredComponents[role] = component;
    }

    return {
      app,
      refresh() {
        vm.refresh?.();
      },
      setPage(pageId) {
        vm.setPage?.(pageId);
      },
      setTheme(patch, opts) {
        vm.setTheme?.(patch, opts);
      },
      registerAtomRenderer,
      unregisterAtomRenderer(role) {
        if (typeof role !== "string" || !role) {
          return;
        }
        delete registeredComponents[role];
      },
      get state() {
        return vm.state;
      },
      get theme() {
        return vm.runtimeTheme;
      },
      sendEvent(message) {
        return vm.sendEvent?.(message) ?? false;
      },
      reconnectEvents() {
        vm.reconnectEvents?.();
      },
      disconnectEvents() {
        vm.disconnectEvents?.();
      },
      registerPlugin(plugin) {
        pluginManager.register(plugin);
      },
      unregisterPlugin(plugin) {
        pluginManager.unregister(plugin);
      },
      get plugins() {
        return {
          list: () => pluginManager.list(),
          register: (plugin) => pluginManager.register(plugin),
          unregister: (plugin) => pluginManager.unregister(plugin),
        };
      },
      events: {
        get state() {
          return vm.eventsState ?? null;
        },
        reconnect() {
          vm.reconnectEvents?.();
        },
        disconnect() {
          vm.disconnectEvents?.();
        },
        send(message) {
          return vm.sendEvent?.(message) ?? false;
        },
      },
      unmount() {
        app.unmount();
      },
    };
  }

  return {
    createLayoutApp,
    DashboardApp,
    TileHost,
    computeGridPlacement,
  };
}
