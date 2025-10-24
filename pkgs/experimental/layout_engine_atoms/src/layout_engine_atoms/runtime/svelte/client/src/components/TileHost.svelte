<script>
  import { computeGridPlacement } from "../../core/index.js";

  export let tile;
  export let grid = null;
  export let viewport = null;
  export let components = {};
  export let baseRenderers = {};

  $: registry = {
    ...(baseRenderers ?? {}),
    ...(components ?? {}),
  };

  $: renderer =
    registry?.[tile?.role] ??
    registry?.default ??
    baseRenderers?.default ??
    null;

  function styleObjectToString(style) {
    if (!style) {
      return "";
    }
    return Object.entries(style)
      .filter(([, value]) => value !== undefined && value !== null)
      .map(([key, value]) => {
        const kebab = key.replace(/([A-Z])/g, "-$1").toLowerCase();
        return `${kebab}: ${value}`;
      })
      .join("; ");
  }

  $: placementStyle = styleObjectToString(
    computeGridPlacement(tile?.frame, grid, viewport),
  );
</script>

<div class="tile" style={placementStyle}>
  {#if renderer}
    <svelte:component this={renderer} {tile} />
  {:else}
    <div class="tile__fallback">
      No renderer registered for role "{tile?.role ?? "unknown"}"
    </div>
  {/if}
</div>
