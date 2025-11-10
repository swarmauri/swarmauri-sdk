<script lang="ts">
  import type { Writable } from "svelte/store";
  import type { LayoutManifest, AtomRegistryMap } from "../types";
  import type { MuxContext } from "../events";
  import { createLayoutContext } from "../context";

  export let manifest: Writable<LayoutManifest>;
  export let registry: Writable<AtomRegistryMap>;
  export let mux: MuxContext | undefined = undefined;

  createLayoutContext({ manifest, registry, mux });
</script>

<slot />
