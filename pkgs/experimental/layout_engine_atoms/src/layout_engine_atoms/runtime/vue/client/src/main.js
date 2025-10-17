import * as Vue from "https://unpkg.com/vue@3/dist/vue.esm-browser.js";
import { atomRenderers } from "./atoms.js";
import { createRuntime } from "./runtime-core.js";

const runtime = createRuntime(Vue, { atomRenderers });

const defaultManifestUrl =
  typeof window !== "undefined" && window.__LE_MANIFEST_URL__
    ? window.__LE_MANIFEST_URL__
    : new URL("manifest.json", window.location.href).toString();

const controller = runtime.createLayoutApp({
  target: "#app",
  manifestUrl: defaultManifestUrl,
  onError(error) {
    console.error("[layout-engine-vue] manifest error", error);
  },
});

if (typeof window !== "undefined") {
  window.LayoutEngineVue = {
    createLayoutApp: runtime.createLayoutApp,
    DashboardApp: runtime.DashboardApp,
    TileHost: runtime.TileHost,
    controller,
  };
}
