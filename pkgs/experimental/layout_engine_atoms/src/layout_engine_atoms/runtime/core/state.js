import { manifestFromPayload } from "./manifest.js";
import { deepMerge, isPlainObject } from "./utils.js";
import { resolveManifestPage } from "./pages.js";

const defaultFetch =
  typeof globalThis !== "undefined" && typeof globalThis.fetch === "function"
    ? globalThis.fetch.bind(globalThis)
    : null;

function createEmptyView() {
  return {
    grid: null,
    tiles: [],
    viewport: null,
    page: null,
    pages: [],
  };
}

export function createRuntimeState(options = {}) {
  let manifestUrl = options.manifestUrl ?? null;
  let fetcher = options.fetcher ?? defaultFetch;
  let fetchOptions = options.fetchOptions ?? {};
  let resolvePageFn =
    typeof options.resolvePage === "function" ? options.resolvePage : null;

  const state = {
    manifest: null,
    loading: options.initiallyLoading ?? true,
    error: null,
    pageId: options.initialPageId ?? null,
    view: createEmptyView(),
  };

  const listeners = new Set();

  function notify() {
    for (const listener of listeners) {
      try {
        listener(state);
      } catch (error) {
        console.error("[layout-engine] runtime listener error", error);
      }
    }
  }

  function syncView() {
    const manifest = state.manifest;
    if (!manifest) {
      state.view = createEmptyView();
      return state.view;
    }
    const page = resolveManifestPage(manifest, state.pageId, resolvePageFn);
    const tiles = (page?.tiles ?? manifest.tiles ?? []).slice();
    const grid = page?.grid ?? manifest.grid ?? null;
    const viewport = page?.viewport ?? manifest.viewport ?? null;
    const pages = Array.isArray(manifest.pages) ? manifest.pages : [];
    const nextPageId =
      page?.id ?? page?.slug ?? page?.name ?? state.pageId ?? null;
    state.pageId = nextPageId;
    state.view = {
      grid,
      tiles,
      viewport,
      page: page ?? null,
      pages,
    };
    return state.view;
  }

  function setManifest(manifest) {
    state.manifest = manifest;
    state.error = null;
    state.loading = false;
    syncView();
    notify();
    return manifest;
  }

  function setError(error) {
    const normalized =
      error instanceof Error ? error : new Error(String(error ?? "Unknown error"));
    state.error = normalized;
    state.loading = false;
    notify();
    return normalized;
  }

  function setLoading(flag) {
    state.loading = Boolean(flag);
    notify();
  }

  function setManifestUrl(url) {
    manifestUrl = url ?? null;
  }

  function setResolvePage(nextResolver) {
    resolvePageFn = typeof nextResolver === "function" ? nextResolver : null;
    syncView();
    notify();
  }

  function setFetcher(nextFetcher, nextOptions) {
    if (typeof nextFetcher === "function") {
      fetcher = nextFetcher;
    }
    if (nextOptions !== undefined) {
      fetchOptions = nextOptions ?? {};
    }
  }

  function setPage(pageId) {
    state.pageId = pageId ?? null;
    const view = syncView();
    notify();
    return view.page;
  }

  async function fetchManifest(urlOverride, overrideOptions) {
    const targetUrl = urlOverride ?? manifestUrl;
    if (!targetUrl) {
      throw new Error("manifestUrl is not set");
    }
    if (typeof fetcher !== "function") {
      throw new Error("fetcher is not available in this environment");
    }
    setLoading(true);
    try {
      const response = await fetcher(targetUrl, {
        ...fetchOptions,
        ...(overrideOptions ?? {}),
      });
      if (!response || typeof response.ok !== "boolean") {
        throw new Error("fetcher must return a Response-like object");
      }
      if (!response.ok) {
        const error = new Error(
          `Failed to fetch manifest (${response.status} ${response.statusText})`,
        );
        error.response = response;
        throw error;
      }
      const payload = await response.json();
      const manifest = manifestFromPayload(payload);
      if (!manifest || typeof manifest !== "object") {
        throw new Error("Fetched payload did not contain a layout manifest");
      }
      setManifest(manifest);
      return manifest;
    } catch (error) {
      setError(error);
      throw error;
    }
  }

  function applyPatch(patch) {
    if (!state.manifest || !isPlainObject(patch)) {
      return state.manifest;
    }
    const merged = deepMerge(state.manifest, patch);
    setManifest(merged);
    return merged;
  }

  function handleManifestPayload(payload) {
    const manifest = manifestFromPayload(payload);
    if (!manifest) {
      return null;
    }
    return setManifest(manifest);
  }

  function subscribe(listener) {
    if (typeof listener === "function") {
      listeners.add(listener);
    }
    return () => {
      listeners.delete(listener);
    };
  }

  function getSummary() {
    const tiles = state.view.tiles ?? [];
    const roles = new Set(tiles.map((tile) => tile.role));
    return {
      tileCount: tiles.length,
      roleCount: roles.size,
    };
  }

  return {
    state,
    subscribe,
    fetchManifest,
    setManifest,
    setError,
    setLoading,
    setPage,
    setManifestUrl,
    setResolvePage,
    setFetcher,
    applyPatch,
    handleManifestPayload,
    syncView,
    getSummary,
    get manifestUrl() {
      return manifestUrl;
    },
    get resolvePage() {
      return resolvePageFn;
    },
  };
}
