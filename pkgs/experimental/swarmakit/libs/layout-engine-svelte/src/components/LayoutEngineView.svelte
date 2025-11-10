<script lang="ts">
  import { derived } from "svelte/store";
  import { useManifestStore, useRegistryStore } from "../context";

  const manifest = useManifestStore();
  const registry = useRegistryStore();
  const tiles = derived(manifest, ($manifest) => $manifest.tiles ?? []);
  const viewportWidth = derived(manifest, ($manifest) =>
    $manifest.viewport?.width ? `${$manifest.viewport.width}px` : "100%",
  );
  const viewportHeight = derived(manifest, ($manifest) =>
    $manifest.viewport?.height ? `${$manifest.viewport.height}px` : "auto",
  );

  const frameStyle = (frame?: { x: number; y: number; w: number; h: number }) => {
    if (!frame) {
      return "";
    }
    return `
      position:absolute;
      left:${frame.x}px;
      top:${frame.y}px;
      width:${frame.w}px;
      height:${frame.h}px;
      box-sizing:border-box;
      padding:12px;
      display:flex;
    `;
  };
</script>

<div class="layout-engine-view" style="position: relative; width: {$viewportWidth}; min-height: {$viewportHeight}">
  {#each $tiles as tile (tile.id)}
    {#if $registry.get(tile.role)}
      {#key tile.id}
        <div class="layout-engine-tile" style={frameStyle(tile.frame)}>
          <svelte:component this={$registry.get(tile.role)?.component} {...tile.props} />
        </div>
      {/key}
    {:else}
      <!-- missing atom -->
    {/if}
  {/each}
</div>
