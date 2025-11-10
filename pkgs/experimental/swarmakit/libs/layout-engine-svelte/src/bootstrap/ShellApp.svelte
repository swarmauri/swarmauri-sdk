<script lang="ts">
  import LayoutEngineProvider from "../components/LayoutEngineProvider.svelte";
  import LayoutEngineShell from "../components/LayoutEngineShell.svelte";
  import type { Writable } from "svelte/store";
  import type { LayoutManifest, AtomRegistryMap } from "../types";
  import type { MuxContext } from "../events";

  export let manifestStore: Writable<LayoutManifest>;
  export let registryStore: Writable<AtomRegistryMap>;
  export let mux: MuxContext | undefined = undefined;
  export let headerSlot: string | null = null;
  export let contentSlot: string | null = null;
  export let footerSlot: string | null = null;

  const renderHTML = (node: HTMLElement, html: string | null) => {
    node.innerHTML = html ?? "";
    return {
      update(value: string | null) {
        node.innerHTML = value ?? "";
      },
      destroy() {
        node.innerHTML = "";
      },
    };
  };
</script>

<LayoutEngineProvider manifest={manifestStore} registry={registryStore} {mux}>
  <div class="le-shell-app">
    {#if headerSlot}
      <div class="le-shell__header" use:renderHTML={headerSlot}></div>
    {/if}

    {#if contentSlot}
      <div class="le-shell__content" use:renderHTML={contentSlot}></div>
    {:else}
      <LayoutEngineShell />
    {/if}

    {#if footerSlot}
      <div class="le-shell__footer" use:renderHTML={footerSlot}></div>
    {/if}
  </div>
</LayoutEngineProvider>

<style>
  .le-shell-app {
    min-height: 100%;
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }
</style>
