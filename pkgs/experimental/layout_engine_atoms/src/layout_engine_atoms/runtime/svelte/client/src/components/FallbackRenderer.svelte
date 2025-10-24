<script>
  export let tile = {};
</script>

<div class="atom atom--fallback">
  <h3 class="atom__title">{tile?.props?.label ?? tile?.role ?? "Tile"}</h3>
  <pre class="atom__debug">{JSON.stringify(tile, null, 2)}</pre>
</div>
