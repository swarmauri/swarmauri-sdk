// Layout Engine Vue Runtime
// Main entry point - re-exports all modules for backward compatibility

// Re-export websocket module
export {
  WSMuxClient,
  createMuxContext,
  useMux,
  muxKey,
} from "./websocket.js";

// Re-export events module
export {
  EVENT_LISTENER_ALIASES,
  DEFAULT_EVENT_METHOD,
  ensureTileProps,
  resolveSlotContent,
  attachTileEventHandlers,
  attachCardActionHandlers,
} from "./events.js";

// Re-export core module
export {
  loadManifest,
  createLayoutEnginePlugin,
  useLayoutManifest,
  useAtomRegistry,
  useMuxContext,
  useEventContext,
  createLayoutEngineApp,
  useSiteNavigation,
} from "./core.js";

// Re-export components module
export {
  LayoutEngineView,
  LayoutEngineShell,
  LayoutEngineNavLink,
} from "./components.js";
