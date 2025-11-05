import { App, inject, Plugin } from "vue";
import type { LayoutManifest, AtomRegistryMap } from "./types";
import type { MuxContext } from "./events";

const MANIFEST_KEY = Symbol("layout-engine:manifest");
const REGISTRY_KEY = Symbol("layout-engine:registry");
const MUX_KEY = Symbol("layout-engine:mux");

export function createLayoutEnginePlugin(
  manifest: LayoutManifest,
  registry: AtomRegistryMap,
  mux?: MuxContext
): Plugin {
  return {
    install(app: App) {
      app.provide(MANIFEST_KEY, manifest);
      app.provide(REGISTRY_KEY, registry);
       if (mux) {
        app.provide(MUX_KEY, mux);
      }
    },
  };
}

export function useLayoutManifest(): LayoutManifest {
  const manifest = inject<LayoutManifest>(MANIFEST_KEY);
  if (!manifest) {
    throw new Error("Layout manifest not found; did you install createLayoutEnginePlugin?");
  }
  return manifest;
}

export function useAtomRegistry(): AtomRegistryMap {
  const registry = inject<AtomRegistryMap>(REGISTRY_KEY);
  if (!registry) {
    throw new Error("Atom registry not found; did you install createLayoutEnginePlugin?");
  }
  return registry;
}

export function useMuxContext(): MuxContext {
  const mux = inject<MuxContext | undefined>(MUX_KEY);
  if (!mux) {
    throw new Error("Mux context not provided; pass a 'mux' option to createLayoutEngineApp.");
  }
  return mux;
}
