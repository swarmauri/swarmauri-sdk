import LayoutEngineDashboard from "./components/LayoutEngineDashboard.svelte";
import TileHost from "./components/TileHost.svelte";
import { createPluginManager, mergeTheme, SWISS_GRID_THEME } from "../core/index.js";
import { createAtomRenderers } from "./atom-renderers.js";
import { computeGridPlacement } from "../core/index.js";

function resolveMountTarget(selectorOrElement) {
  const HTMLElementRef =
    typeof HTMLElement !== "undefined" ? HTMLElement : null;
  if (
    HTMLElementRef &&
    selectorOrElement instanceof HTMLElementRef
  ) {
    return selectorOrElement;
  }
  if (typeof selectorOrElement === "string" && selectorOrElement) {
    if (typeof document === "undefined") {
      return null;
    }
    return document.querySelector(selectorOrElement);
  }
  return selectorOrElement ?? null;
}

export function createRuntime(svelteExports, options = {}) {
  const { setContext, getContext, onMount, onDestroy } = svelteExports ?? {};
  if (!setContext || !getContext || !onMount || !onDestroy) {
    throw new Error(
      "createRuntime requires Svelte lifecycle exports (setContext, getContext, onMount, onDestroy).",
    );
  }

  const stores = options.stores ?? {};
  const { writable, derived, get } = stores;
  if (!writable || !derived || !get) {
    throw new Error(
      "createRuntime requires Svelte store helpers (writable, derived, get).",
    );
  }

  const defaultRenderers = createAtomRenderers();
  const rendererOverrides =
    options.atomRenderers && typeof options.atomRenderers === "object"
      ? options.atomRenderers
      : {};
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

  function createPluginManagerInstance() {
    return createPluginManager(basePluginList);
  }

  const runtimeConfig = {
    baseRenderers,
    defaultTheme,
  };

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

    const registeredComponents = { ...componentsOverride };
    const pluginManager = createPluginManagerInstance();
    runtimePlugins.forEach((plugin) => pluginManager.register(plugin));

    const mountTarget = resolveMountTarget(targetSelector);
    if (!mountTarget) {
      throw new Error(
        `Unable to find mount target "${targetSelector}". Ensure the element exists.`,
      );
    }

    const app = new LayoutEngineDashboard({
      target: mountTarget,
      props: {
        runtime: runtimeConfig,
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
      },
    });

    function registerAtomRenderer(role, component) {
      if (typeof role !== "string" || !role) {
        return;
      }
      if (component === undefined || component === null) {
        delete registeredComponents[role];
      } else {
        registeredComponents[role] = component;
      }
      app.$set({ components: { ...registeredComponents } });
    }

    return {
      app,
      refresh() {
        return app.refresh?.();
      },
      setPage(pageId) {
        return app.setPage?.(pageId);
      },
      setTheme(patch, opts) {
        return app.setTheme?.(patch, opts);
      },
      registerAtomRenderer,
      unregisterAtomRenderer(role) {
        registerAtomRenderer(role, null);
      },
      get state() {
        return app.getState?.() ?? null;
      },
      get theme() {
        return app.getRuntimeTheme?.() ?? null;
      },
      sendEvent(message) {
        return app.sendEvent?.(message) ?? false;
      },
      reconnectEvents() {
        app.reconnectEvents?.();
      },
      disconnectEvents() {
        app.disconnectEvents?.();
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
          return app.getEventsState?.() ?? null;
        },
        reconnect() {
          app.reconnectEvents?.();
        },
        disconnect() {
          app.disconnectEvents?.();
        },
        send(message) {
          return app.sendEvent?.(message) ?? false;
        },
      },
      unmount() {
        app.$destroy();
      },
    };
  }

  return {
    createLayoutApp,
    DashboardApp: LayoutEngineDashboard,
    LayoutEngineDashboard,
    TileHost,
    computeGridPlacement,
  };
}
