// Core Module
// Contains loader, plugin system, app factory, and navigation

import {
  computed,
  inject,
  isRef,
  markRaw,
  reactive,
  ref,
  toRefs,
  watchEffect,
} from "vue";
import { createMuxContext } from "./websocket.js";

// ============================================================================
// MANIFEST LOADER
// ============================================================================

const manifestCache = /* @__PURE__ */ new Map();
const componentCache = /* @__PURE__ */ new Map();

/**
 * Default fetcher for manifest JSON
 */
async function defaultFetcher(url) {
  const res = await fetch(url);
  if (!res.ok) {
    throw new Error(`Failed to fetch manifest: ${res.status} ${res.statusText}`);
  }
  return await res.json();
}

/**
 * Default resolver for dynamic imports of atom modules
 */
async function defaultImportResolver(atom) {
  if (!atom.module) {
    throw new Error(`Missing module specifier for atom ${atom.role}`);
  }
  const mod = await import(
    /* @vite-ignore */
    atom.module
  );
  const exportName = atom.export ?? "default";
  if (!(exportName in mod)) {
    throw new Error(`Export '${exportName}' not found in module ${atom.module}`);
  }
  return mod[exportName];
}

/**
 * Generate cache key from manifest metadata
 */
function cacheKeyFromManifest(manifest, explicit) {
  if (explicit) return explicit;
  const version = manifest.meta?.atoms && typeof manifest.meta.atoms === "object" ? manifest.meta.atoms["revision"] : void 0;
  return String(version ?? manifest.etag ?? manifest.version ?? "default");
}

/**
 * Load manifest and resolve all atom components
 */
async function loadManifest(manifestUrl, options = {}) {
  const fetcher = options.fetcher ?? defaultFetcher;
  const loader = options.importResolver ?? defaultImportResolver;
  const manifest = await fetcher(manifestUrl);
  const cacheKey = cacheKeyFromManifest(manifest, options.cacheKey);
  if (manifestCache.has(cacheKey)) {
    const cachedManifest = manifestCache.get(cacheKey);
    const cachedComponents = componentCache.get(cacheKey) ?? /* @__PURE__ */ new Map();
    return { manifest: cachedManifest, components: cachedComponents };
  }
  const registry = /* @__PURE__ */ new Map();
  const swarmaAtoms = manifest.tiles.map((tile) => tile.atom).filter((atom) => Boolean(atom && atom.family === "swarmakit"));
  for (const atom of swarmaAtoms) {
    if (registry.has(atom.role)) continue;
    const component = await loader(atom);
    registry.set(atom.role, { component: markRaw(component), atom });
  }
  manifestCache.set(cacheKey, manifest);
  componentCache.set(cacheKey, registry);
  return { manifest, components: registry };
}

// ============================================================================
// PLUGIN SYSTEM
// ============================================================================

const MANIFEST_KEY = Symbol("layout-engine:manifest");
const REGISTRY_KEY = Symbol("layout-engine:registry");
const MUX_KEY = Symbol("layout-engine:mux");
const EVENTS_KEY = Symbol("layout-engine:events");

/**
 * Create Vue plugin that provides manifest, registry, mux, and events context
 */
function createLayoutEnginePlugin(manifest, registry, options = {}) {
  return {
    install(app) {
      app.provide(MANIFEST_KEY, manifest);
      app.provide(REGISTRY_KEY, registry);
      if (options.mux) {
        app.provide(MUX_KEY, options.mux);
      }
      if (options.events) {
        app.provide(EVENTS_KEY, options.events);
      }
    }
  };
}

/**
 * Composable to access layout manifest
 */
function useLayoutManifest() {
  const manifest = inject(MANIFEST_KEY);
  if (!manifest) {
    throw new Error("Layout manifest not found; did you install createLayoutEnginePlugin?");
  }
  return manifest;
}

/**
 * Composable to access atom registry
 */
function useAtomRegistry() {
  const registry = inject(REGISTRY_KEY);
  if (!registry) {
    throw new Error("Atom registry not found; did you install createLayoutEnginePlugin?");
  }
  return registry;
}

/**
 * Composable to access mux context (WebSocket multiplexer)
 */
function useMuxContext() {
  const mux = inject(MUX_KEY);
  if (!mux) {
    throw new Error("Mux context not provided; pass a 'mux' option to createLayoutEngineApp.");
  }
  return mux;
}

/**
 * Composable to access events context
 */
function useEventContext(optional = true) {
  const events = inject(EVENTS_KEY, null);
  if (!events && !optional) {
    throw new Error("Event context not provided; ensure events are enabled in the shell.");
  }
  return events;
}

// ============================================================================
// APP FACTORY
// ============================================================================

/**
 * Create a complete layout engine app with manifest, components, and optional mux
 */
async function createLayoutEngineApp(options) {
  const { manifest, components } = await loadManifest(options.manifestUrl);
  const mux = options.muxUrl ? createMuxContext({
    manifest,
    muxUrl: options.muxUrl,
    protocols: options.muxProtocols
  }) : void 0;
  const manifestRef = ref(manifest);
  const registryRef = ref(components);
  const tiles = computed(() => manifestRef.value.tiles);
  const plugin = createLayoutEnginePlugin(manifestRef.value, registryRef.value, { mux });
  return {
    plugin,
    manifest: manifestRef,
    tiles,
    components: registryRef,
    mux
  };
}

// ============================================================================
// SITE NAVIGATION
// ============================================================================

/**
 * Normalize site metadata from manifest
 */
function normaliseSite(manifest) {
  const site = manifest.site;
  if (!site) {
    return { pages: [], activePageId: null, basePath: void 0 };
  }
  const pages = Array.isArray(site.pages) ? site.pages.map((page) => ({
    id: String(page?.id ?? ""),
    route: String(page?.route ?? "/"),
    title: page?.title ? String(page.title) : void 0,
    slots: Array.isArray(page?.slots) ? page?.slots : void 0
  })) : [];
  return {
    pages,
    activePageId: site.active_page ?? site?.["activePage"],
    basePath: site.navigation && typeof site.navigation === "object" ? site.navigation["base_path"] : void 0
  };
}

/**
 * Composable for site-level navigation
 */
function useSiteNavigation(manifest) {
  const getManifest = () => isRef(manifest) ? manifest.value : manifest;
  const state = reactive(normaliseSite(getManifest()));
  watchEffect(() => {
    const next = normaliseSite(getManifest());
    state.pages = next.pages;
    state.activePageId = next.activePageId;
    state.basePath = next.basePath;
  });
  const activePage = computed(
    () => state.pages.find((page) => page.id === state.activePageId) ?? null
  );
  const navigate = (pageId) => {
    const page = state.pages.find((p) => p.id === pageId);
    if (!page) return null;
    state.activePageId = page.id;
    return page.route;
  };
  return {
    ...toRefs(state),
    activePage,
    navigate
  };
}

// Exports
export {
  loadManifest,
  createLayoutEnginePlugin,
  useLayoutManifest,
  useAtomRegistry,
  useMuxContext,
  useEventContext,
  createLayoutEngineApp,
  useSiteNavigation,
};
