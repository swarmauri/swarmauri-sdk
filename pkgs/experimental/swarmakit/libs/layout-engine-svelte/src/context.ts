import { getContext, setContext } from "svelte";
import type { Writable } from "svelte/store";
import type { AtomRegistryMap, LayoutManifest } from "./types";
import type { MuxContext } from "./events";

const MANIFEST_KEY = Symbol("layout-engine:manifest");
const REGISTRY_KEY = Symbol("layout-engine:registry");
const MUX_KEY = Symbol("layout-engine:mux");

type LayoutContext = {
  manifest: Writable<LayoutManifest>;
  registry: Writable<AtomRegistryMap>;
  mux?: MuxContext;
};

export function createLayoutContext(context: LayoutContext): void {
  setContext(MANIFEST_KEY, context.manifest);
  setContext(REGISTRY_KEY, context.registry);
  if (context.mux) {
    setContext(MUX_KEY, context.mux);
  }
}

export function useManifestStore(): Writable<LayoutManifest> {
  const store = getContext<Writable<LayoutManifest>>(MANIFEST_KEY);
  if (!store) {
    throw new Error("Layout manifest store not found; wrap content in LayoutEngineProvider.");
  }
  return store;
}

export function useRegistryStore(): Writable<AtomRegistryMap> {
  const store = getContext<Writable<AtomRegistryMap>>(REGISTRY_KEY);
  if (!store) {
    throw new Error("Atom registry store not found; wrap content in LayoutEngineProvider.");
  }
  return store;
}

export function useMuxContext(): MuxContext {
  const mux = getContext<MuxContext | undefined>(MUX_KEY);
  if (!mux) {
    throw new Error("Mux context not provided; pass mux to LayoutEngineProvider.");
  }
  return mux;
}
