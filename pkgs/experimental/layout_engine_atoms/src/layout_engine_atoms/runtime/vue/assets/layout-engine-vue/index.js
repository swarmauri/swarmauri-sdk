// src/composables.ts
import { computed, ref as ref2 } from "vue";

// src/loader.ts
import { markRaw } from "vue";
var manifestCache = /* @__PURE__ */ new Map();
var componentCache = /* @__PURE__ */ new Map();
async function defaultFetcher(url) {
  const res = await fetch(url);
  if (!res.ok) {
    throw new Error(`Failed to fetch manifest: ${res.status} ${res.statusText}`);
  }
  return await res.json();
}
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
function cacheKeyFromManifest(manifest, explicit) {
  if (explicit) return explicit;
  const version = manifest.meta?.atoms && typeof manifest.meta.atoms === "object" ? manifest.meta.atoms["revision"] : void 0;
  return String(version ?? manifest.etag ?? manifest.version ?? "default");
}
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

// src/plugin.ts
import { inject } from "vue";
var MANIFEST_KEY = Symbol("layout-engine:manifest");
var REGISTRY_KEY = Symbol("layout-engine:registry");
var MUX_KEY = Symbol("layout-engine:mux");
function createLayoutEnginePlugin(manifest, registry, mux) {
  return {
    install(app) {
      app.provide(MANIFEST_KEY, manifest);
      app.provide(REGISTRY_KEY, registry);
      if (mux) {
        app.provide(MUX_KEY, mux);
      }
    }
  };
}
function useLayoutManifest() {
  const manifest = inject(MANIFEST_KEY);
  if (!manifest) {
    throw new Error("Layout manifest not found; did you install createLayoutEnginePlugin?");
  }
  return manifest;
}
function useAtomRegistry() {
  const registry = inject(REGISTRY_KEY);
  if (!registry) {
    throw new Error("Atom registry not found; did you install createLayoutEnginePlugin?");
  }
  return registry;
}
function useMuxContext() {
  const mux = inject(MUX_KEY);
  if (!mux) {
    throw new Error("Mux context not provided; pass a 'mux' option to createLayoutEngineApp.");
  }
  return mux;
}

// src/events.ts
import { onBeforeUnmount } from "vue";

// src/mux.ts
import EventEmitter from "eventemitter3";
var DEFAULT_RECONNECT_DELAY = 1e3;
var DEFAULT_MAX_DELAY = 1e4;
var DEFAULT_BACKOFF = 1.7;
var WSMuxClient = class extends EventEmitter {
  constructor(options) {
    super();
    this.socket = null;
    this.reconnectTimer = null;
    this.subscriptions = /* @__PURE__ */ new Map();
    this.pendingSubscribes = /* @__PURE__ */ new Set();
    this.outboundQueue = [];
    this.handleOpen = () => {
      this.emit("open");
      this.reconnectDelay = this.options.reconnectDelay;
      while (this.outboundQueue.length) {
        const message = this.outboundQueue.shift();
        if (message) {
          this.socket?.send(JSON.stringify(message));
        }
      }
      this.flushSubscribes();
    };
    this.handleMessage = (event) => {
      try {
        const data = JSON.parse(String(event.data));
        if (!data || typeof data !== "object" || !("channel" in data)) {
          this.emit("raw", data);
          return;
        }
        const channelId = String(data["channel"] ?? "");
        if (!channelId) return;
        this.emit("message", data);
        const handlers = this.subscriptions.get(channelId);
        if (!handlers) return;
        const message = {
          channel: channelId,
          payload: data["payload"],
          ...data
        };
        for (const handler of handlers) {
          handler(message);
        }
      } catch (err) {
        this.emit("error", err);
      }
    };
    this.handleClose = () => {
      this.emit("close");
      this.scheduleReconnect();
    };
    this.handleError = (event) => {
      this.emit("error", event);
    };
    if (!options.url) {
      throw new Error("WSMuxClient requires a url");
    }
    this.options = {
      protocols: options.protocols ?? [],
      reconnectDelay: options.reconnectDelay ?? DEFAULT_RECONNECT_DELAY,
      maxReconnectDelay: options.maxReconnectDelay ?? DEFAULT_MAX_DELAY,
      backoffFactor: options.backoffFactor ?? DEFAULT_BACKOFF,
      url: options.url
    };
    this.reconnectDelay = this.options.reconnectDelay;
  }
  connect() {
    if (this.socket && (this.socket.readyState === WebSocket.OPEN || this.socket.readyState === WebSocket.CONNECTING)) {
      return;
    }
    this.clearReconnect();
    this.socket = new WebSocket(this.options.url, this.options.protocols);
    this.socket.addEventListener("open", this.handleOpen);
    this.socket.addEventListener("message", this.handleMessage);
    this.socket.addEventListener("close", this.handleClose);
    this.socket.addEventListener("error", this.handleError);
  }
  disconnect() {
    this.clearReconnect();
    if (this.socket) {
      this.socket.removeEventListener("open", this.handleOpen);
      this.socket.removeEventListener("message", this.handleMessage);
      this.socket.removeEventListener("close", this.handleClose);
      this.socket.removeEventListener("error", this.handleError);
      this.socket.close();
      this.socket = null;
    }
  }
  subscribe(channelId, handler) {
    if (!this.subscriptions.has(channelId)) {
      this.subscriptions.set(channelId, /* @__PURE__ */ new Set());
      this.enqueueSubscribe(channelId);
    }
    const set = this.subscriptions.get(channelId);
    set.add(handler);
    this.connect();
    return () => {
      const group = this.subscriptions.get(channelId);
      if (!group) return;
      group.delete(handler);
      if (group.size === 0) {
        this.subscriptions.delete(channelId);
        this.enqueueUnsubscribe(channelId);
      }
    };
  }
  publish(channelId, payload) {
    this.send({ action: "publish", channel: channelId, payload });
  }
  enqueueSubscribe(channelId) {
    this.pendingSubscribes.add(channelId);
    this.send({ action: "subscribe", channel: channelId });
  }
  enqueueUnsubscribe(channelId) {
    this.send({ action: "unsubscribe", channel: channelId });
  }
  flushSubscribes() {
    for (const channelId of this.subscriptions.keys()) {
      this.send({ action: "subscribe", channel: channelId });
    }
    this.pendingSubscribes.clear();
  }
  send(message) {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify(message));
    } else {
      this.outboundQueue.push(message);
      this.connect();
    }
  }
  scheduleReconnect() {
    this.clearReconnect();
    this.reconnectTimer = setTimeout(() => {
      this.connect();
      this.reconnectDelay = Math.min(
        this.reconnectDelay * this.options.backoffFactor,
        this.options.maxReconnectDelay
      );
    }, this.reconnectDelay);
  }
  clearReconnect() {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
  }
};

// src/events.ts
var muxKey = Symbol("layout-engine:mux");
function createMuxContext(options) {
  const client = new WSMuxClient({ url: options.muxUrl, protocols: options.protocols });
  client.connect();
  return {
    client,
    channels: options.manifest.channels ?? []
  };
}
function useMux(mux, channelId, handler) {
  const unsubscribe = mux.client.subscribe(channelId, handler);
  onBeforeUnmount(() => unsubscribe());
  return {
    publish: (payload) => mux.client.publish(channelId, payload)
  };
}

// src/composables.ts
async function createLayoutEngineApp(options) {
  const { manifest, components } = await loadManifest(options.manifestUrl);
  const mux = options.muxUrl ? createMuxContext({
    manifest,
    muxUrl: options.muxUrl,
    protocols: options.muxProtocols
  }) : void 0;
  const manifestRef = ref2(manifest);
  const registryRef = ref2(components);
  const tiles = computed(() => manifestRef.value.tiles);
  const plugin = createLayoutEnginePlugin(manifestRef.value, registryRef.value, mux);
  return {
    plugin,
    manifest: manifestRef,
    tiles,
    components: registryRef,
    mux
  };
}

// src/site.ts
import { computed as computed2, isRef, reactive, toRefs, watchEffect } from "vue";
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
function useSiteNavigation(manifest) {
  const getManifest = () => isRef(manifest) ? manifest.value : manifest;
  const state = reactive(normaliseSite(getManifest()));
  watchEffect(() => {
    const next = normaliseSite(getManifest());
    state.pages = next.pages;
    state.activePageId = next.activePageId;
    state.basePath = next.basePath;
  });
  const activePage = computed2(
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

// src/components/LayoutEngineView.ts
import { defineComponent, h } from "vue";
var LayoutEngineView_default = defineComponent({
  name: "LayoutEngineView",
  setup(_, { slots }) {
    const manifest = useLayoutManifest();
    const registry = useAtomRegistry();
    const site = useSiteNavigation(manifest);
    const renderTiles = () => {
      if (!manifest.tiles.length) {
        return [];
      }
      const nodes = [];
      for (const tile of manifest.tiles) {
        const entry = registry.get(tile.role);
        if (!entry) {
          console.warn(`Atom '${tile.role}' not registered in registry`);
          continue;
        }
        const frame = tile.frame ?? { x: 0, y: 0, w: 0, h: 0 };
        const style = {
          position: "absolute",
          left: `${frame.x}px`,
          top: `${frame.y}px`,
          width: `${frame.w}px`,
          height: `${frame.h}px`,
          boxSizing: "border-box",
          padding: "12px",
          display: "flex"
        };
        nodes.push(
          h(
            "div",
            { key: tile.id, class: "layout-engine-tile", style },
            [h(entry.component, { ...tile.props })]
          )
        );
      }
      return nodes;
    };
    return () => {
      const viewportWidth = manifest.viewport?.width ?? 0;
      const viewportHeight = manifest.viewport?.height ?? 0;
      if (slots.default) {
        return slots.default({
          manifest,
          site,
          tiles: manifest.tiles,
          components: registry
        });
      }
      return h(
        "div",
        {
          class: "layout-engine-view",
          style: {
            position: "relative",
            width: viewportWidth ? `${viewportWidth}px` : "100%",
            minHeight: viewportHeight ? `${viewportHeight}px` : "auto"
          }
        },
        renderTiles()
      );
    };
  }
});

// src/components/LayoutEngineShell.ts
import { defineComponent as defineComponent2, h as h2 } from "vue";
var LayoutEngineShell_default = defineComponent2({
  name: "LayoutEngineShell",
  setup(_, { slots }) {
    const manifest = useLayoutManifest();
    const site = useSiteNavigation(manifest);
    const defaultSlot = slots.default;
    return () => {
      const nav = site.pages.value;
      const current = site.activePage.value;
      return h2("div", { class: "layout-engine-shell" }, [
        defaultSlot ? defaultSlot({ site, manifest }) : h2(
          "nav",
          { class: "layout-engine-shell__nav" },
          nav.map(
            (page) => h2(
              "button",
              {
                class: [
                  "layout-engine-shell__nav-item",
                  page.id === current?.id && "is-active"
                ],
                onClick: () => site.navigate(page.id)
              },
              page.title ?? page.id
            )
          )
        ),
        h2(LayoutEngineView_default)
      ]);
    };
  }
});

// src/components/NavLink.ts
import { computed as computed3, defineComponent as defineComponent3, h as h3 } from "vue";
var NavLink_default = defineComponent3({
  name: "LayoutEngineNavLink",
  props: {
    pageId: {
      type: String,
      required: true
    }
  },
  setup(props, { slots }) {
    const manifest = useLayoutManifest();
    const site = useSiteNavigation(manifest);
    const page = computed3(() => site.pages.value.find((p) => p.id === props.pageId));
    const onClick = () => site.navigate(props.pageId);
    return () => h3(
      "button",
      {
        class: [
          "layout-engine-nav-link",
          page.value?.id === site.activePage.value?.id && "is-active"
        ],
        onClick
      },
      slots.default ? slots.default() : page.value?.title ?? props.pageId
    );
  }
});
export {
  NavLink_default as LayoutEngineNavLink,
  LayoutEngineShell_default as LayoutEngineShell,
  LayoutEngineView_default as LayoutEngineView,
  WSMuxClient,
  createLayoutEngineApp,
  createLayoutEnginePlugin,
  createMuxContext,
  useAtomRegistry,
  useLayoutManifest,
  useMux,
  useMuxContext,
  useSiteNavigation
};
