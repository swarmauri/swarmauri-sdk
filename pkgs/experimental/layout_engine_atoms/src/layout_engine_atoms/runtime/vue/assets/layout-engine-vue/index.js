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
var EVENTS_KEY = Symbol("layout-engine:events");
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
function useEventContext(optional = true) {
  const events = inject(EVENTS_KEY, null);
  if (!events && !optional) {
    throw new Error("Event context not provided; ensure events are enabled in the shell.");
  }
  return events;
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
  const plugin = createLayoutEnginePlugin(manifestRef.value, registryRef.value, { mux });
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
var EVENT_LISTENER_ALIASES = {
  click: "onClick",
  primary: "onClick",
  secondary: "onClick",
  submit: "onSubmit",
  change: "onChange",
  input: "onInput",
  action: "onAction",
  select: "onSelect",
  broadcast: "onBroadcast",
  increment: "onIncrement",
  primaryaction: "onPrimaryAction",
  secondaryaction: "onSecondaryAction"
};
var DEFAULT_EVENT_METHOD = "POST";
function ensureTileProps(tile) {
  if (!tile.props || typeof tile.props !== "object") {
    tile.props = {};
  }
  return tile.props;
}
function resolveSlotContent(tile, props) {
  const label =
    (typeof props.label === "string" && props.label) ||
    (typeof tile?.props?.label === "string" && tile.props.label);
  const text =
    (typeof props.text === "string" && props.text) ||
    (typeof tile?.props?.text === "string" && tile.props.text);
  const children =
    (typeof props.children === "string" && props.children) ||
    (typeof tile?.props?.children === "string" && tile.props.children);
  return label || text || children || null;
}
function resolveListenerProp(trigger) {
  if (!trigger) {
    return null;
  }
  if (trigger.startsWith("on")) {
    return trigger;
  }
  const normalized = trigger.toLowerCase();
  if (EVENT_LISTENER_ALIASES[normalized]) {
    return EVENT_LISTENER_ALIASES[normalized];
  }
  const fallback = `on${normalized.charAt(0).toUpperCase()}${normalized.slice(1)}`;
  return fallback || "onClick";
}
function ensureTileEventEntry(tile, key, eventId) {
  if (!tile?.props || typeof tile.props !== "object") {
    return null;
  }
  const events = tile.props.events;
  if (!events || typeof events !== "object") {
    tile.props.events = {};
  }
  const store = tile.props.events;
  let current = store[key];
  if (!current || typeof current !== "object") {
    current = { id: eventId };
    store[key] = current;
  }
  if (!current.state) {
    current.state = {};
  }
  return current;
}
function setEventPendingState(tile, binding, isPending) {
  const entry = ensureTileEventEntry(tile, binding.key, binding.id);
  if (entry) {
    entry.state.pending = isPending;
    if (isPending) {
      entry.state.error = null;
    }
  }
  if (binding.loadingProp && tile?.props) {
    tile.props[binding.loadingProp] = isPending;
  }
  if (binding.disabledProp && tile?.props) {
    tile.props[binding.disabledProp] = isPending;
  }
}
function recordEventResult(tile, binding, result) {
  const entry = ensureTileEventEntry(tile, binding.key, binding.id);
  if (entry) {
    entry.state.lastResult = result;
    entry.state.error = null;
  }
}
function recordEventError(tile, binding, error) {
  const entry = ensureTileEventEntry(tile, binding.key, binding.id);
  if (entry) {
    entry.state.error = error;
  }
}
function normalizeTileEventBinding(tile, key, raw, eventsContext) {
  if (!raw) return null;
  const spec = typeof raw === "string" ? { id: raw } : { ...raw };
  const eventId = spec.id ?? spec.event ?? spec.eventId ?? null;
  if (!eventId) {
    return null;
  }
  ensureTileEventEntry(tile, key, eventId);
  const descriptor = eventsContext?.describe ? eventsContext.describe(eventId) : null;
  const trigger = spec.trigger ?? spec.listener ?? key;
  const listener = resolveListenerProp(trigger);
  if (!listener) return null;
  const method = (spec.method ?? descriptor?.method ?? DEFAULT_EVENT_METHOD).toUpperCase();
  return {
    key,
    id: eventId,
    trigger,
    listener,
    method,
    payload: spec.payload ?? {},
    context: spec.context ?? {},
    stateProp: spec.stateProp ?? spec.prop ?? descriptor?.stateProp,
    loadingProp: spec.loadingProp ?? descriptor?.loadingProp,
    disabledProp: spec.disabledProp ?? descriptor?.disabledProp,
    preventDefault: spec.preventDefault ?? trigger === "submit",
    stopPropagation: spec.stopPropagation ?? false
  };
}
function createTileEventHandler(tile, binding, eventsContext, componentProps) {
  if (!eventsContext?.invoke) {
    return null;
  }
  return async (domEvent) => {
    if (binding.preventDefault && domEvent?.preventDefault) {
      domEvent.preventDefault();
    }
    if (binding.stopPropagation && domEvent?.stopPropagation) {
      domEvent.stopPropagation();
    }
    setEventPendingState(tile, binding, true);
    try {
      const payload = { ...(binding.payload ?? {}) };
      const eventValue =
        domEvent && typeof domEvent === "object" && "detail" in domEvent
          ? domEvent.detail
          : domEvent;
      if (typeof eventValue === "boolean") {
        payload.checked = eventValue;
        if (binding.stateProp) {
          if (tile?.props) {
            tile.props[binding.stateProp] = eventValue;
          }
          if (componentProps && typeof componentProps === "object") {
            componentProps[binding.stateProp] = eventValue;
          }
        }
      } else if (
        eventValue &&
        typeof eventValue === "object" &&
        !Array.isArray(eventValue)
      ) {
        Object.assign(payload, eventValue);
        if (binding.stateProp && binding.stateProp in eventValue) {
          if (tile?.props) {
            tile.props[binding.stateProp] = eventValue[binding.stateProp];
          }
          if (componentProps && typeof componentProps === "object") {
            componentProps[binding.stateProp] = eventValue[binding.stateProp];
          }
        }
      }
      const context = {
        tileId: tile.id,
        role: tile.role,
        ...binding.context
      };
      const result = await eventsContext.invoke(binding.id, {
        method: binding.method,
        payload,
        context
      });
      recordEventResult(tile, binding, result?.body ?? result);
      return result;
    } catch (error) {
      recordEventError(tile, binding, error?.body ?? { message: error?.message ?? "Event failed" });
      throw error;
    } finally {
      setEventPendingState(tile, binding, false);
    }
  };
}
function attachTileEventHandlers(tile, props, eventsContext) {
  if (!eventsContext || !props || typeof props !== "object") {
    return props;
  }
  const eventDefs = tile?.props?.events;
  if (!eventDefs || typeof eventDefs !== "object") {
    return props;
  }
  const handlers = {};
  for (const [key, raw] of Object.entries(eventDefs)) {
    const binding = normalizeTileEventBinding(tile, key, raw, eventsContext);
    if (!binding) continue;
    const handler = createTileEventHandler(tile, binding, eventsContext, props);
    if (handler && binding.listener) {
      handlers[binding.listener] = handler;
    }
  }
  if (Object.keys(handlers).length) {
    Object.assign(props, handlers);
    delete props.events;
  }
  return props;
}

function attachCardActionHandlers(tile, props, eventsContext) {
  if (!eventsContext || !props || typeof props !== "object") {
    return props;
  }
  if (tile?.role !== "swarmakit:vue:card-actions") {
    return props;
  }
  const actions = props.actions;
  if (!Array.isArray(actions)) {
    return props;
  }
  actions.forEach((action, actionIndex) => {
    if (!action || typeof action !== "object") {
      return;
    }
    const rawEvents = action.events;
    if (!rawEvents) {
      return;
    }
    const candidates = Array.isArray(rawEvents) ? rawEvents : [rawEvents];
    const handlers = [];
    candidates.forEach((raw, eventIndex) => {
      const binding = normalizeTileEventBinding(
        tile,
        `card-action:${actionIndex}:${eventIndex}`,
        raw,
        eventsContext
      );
      if (!binding) {
        return;
      }
      const handler = createTileEventHandler(tile, binding, eventsContext, props);
      if (handler) {
        handlers.push(handler);
      }
    });
    if (!handlers.length) {
      return;
    }
    action.onClick = async (event) => {
      for (const handler of handlers) {
        await handler(event);
      }
    };
    delete action.events;
  });
  return props;
}
var LayoutEngineView_default = defineComponent({
  name: "LayoutEngineView",
  setup(_, { slots }) {
    const manifest = useLayoutManifest();
    const registry = useAtomRegistry();
    const site = useSiteNavigation(manifest);
    const eventsContext = useEventContext(true);
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
        const componentProps = ensureTileProps(tile);
        const preparedProps = attachTileEventHandlers(
          tile,
          componentProps,
          eventsContext
        );
        const finalProps = attachCardActionHandlers(
          tile,
          preparedProps,
          eventsContext
        );
        const slotContent = resolveSlotContent(tile, finalProps);
        const slotPayload = slotContent
          ? {
            default: () => slotContent,
          }
          : void 0;
        nodes.push(
          h(
            "div",
            { key: tile.id, class: "layout-engine-tile", style },
            [h(entry.component, finalProps, slotPayload)]
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
              minHeight: viewportHeight ? `${viewportHeight}px` : "auto",
              margin: "0 auto",
              overflowY: "auto",
              maxHeight: "100vh",
              paddingBottom: "48px"
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
  loadManifest,
  useAtomRegistry,
  useEventContext,
  useLayoutManifest,
  useMux,
  useMuxContext,
  useSiteNavigation
};
