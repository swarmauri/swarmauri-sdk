import { writable, derived, type Readable, type Writable } from "svelte/store";
import type { LayoutManifest, LayoutTile, LoadedComponent } from "./types";
import { loadManifest } from "./loader";
import { createMuxContext } from "./events";

export type LayoutEngineApp = {
  manifest: Writable<LayoutManifest>;
  tiles: Readable<LayoutTile[]>;
  components: Writable<Map<string, LoadedComponent>>;
  mux?: ReturnType<typeof createMuxContext>;
};

export async function createLayoutEngineApp(options: {
  manifestUrl: string;
  muxUrl?: string;
  muxProtocols?: string | string[];
}): Promise<LayoutEngineApp> {
  const { manifest, components } = await loadManifest(options.manifestUrl);
  const mux = options.muxUrl
    ? createMuxContext({
        manifest,
        muxUrl: options.muxUrl,
        protocols: options.muxProtocols,
      })
    : undefined;

  const manifestStore = writable(manifest);
  const registryStore = writable(components);
  const tiles = derived(manifestStore, ($manifest) => $manifest.tiles ?? []);

  return {
    manifest: manifestStore,
    tiles,
    components: registryStore,
    mux,
  };
}
