import { setContext, getContext, onMount, onDestroy } from "svelte";
import { writable, derived, get } from "svelte/store";
import { createAtomRenderers } from "./atom-renderers.js";
import { createRuntime } from "./runtime-core.js";
import styles from "./styles.css?inline";

function ensureGlobalStyles() {
  if (typeof document === "undefined") {
    return;
  }
  const STYLE_ID = "layout-engine-svelte-styles";
  if (document.getElementById(STYLE_ID)) {
    return;
  }
  const element = document.createElement("style");
  element.id = STYLE_ID;
  element.textContent = styles;
  document.head.appendChild(element);
}

ensureGlobalStyles();

const runtime = createRuntime(
  { setContext, getContext, onMount, onDestroy },
  {
    stores: { writable, derived, get },
    atomRenderers: createAtomRenderers(),
  },
);

export const createLayoutApp = runtime.createLayoutApp;
export const DashboardApp = runtime.DashboardApp;
export const LayoutEngineDashboard = runtime.LayoutEngineDashboard;
export const TileHost = runtime.TileHost;
export const computeGridPlacement = runtime.computeGridPlacement;

export default createLayoutApp;
