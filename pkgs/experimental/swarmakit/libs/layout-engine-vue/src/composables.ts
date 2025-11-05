import { computed, ref, type Component, type Ref } from "vue";
import type { LayoutManifest, LayoutTile, LoadedComponent } from "./types";
import { loadManifest } from "./loader";
import { createLayoutEnginePlugin, useAtomRegistry } from "./plugin";
import { createMuxContext } from "./events";

export type LayoutEngineApp = {
  plugin: ReturnType<typeof createLayoutEnginePlugin>;
  manifest: Ref<LayoutManifest>;
  tiles: Ref<LayoutTile[]>;
  components: Ref<Map<string, LoadedComponent>>;
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
  const manifestRef = ref(manifest);
  const registryRef = ref(components);

  const tiles = computed(() => manifestRef.value.tiles);
  const plugin = createLayoutEnginePlugin(manifestRef.value, registryRef.value, mux);

  return {
    plugin,
    manifest: manifestRef,
    tiles,
    components: registryRef,
    mux,
  };
}

export function useTileComponent(role: string): Component | undefined {
  return useAtomRegistry().get(role)?.component as Component | undefined;
}
