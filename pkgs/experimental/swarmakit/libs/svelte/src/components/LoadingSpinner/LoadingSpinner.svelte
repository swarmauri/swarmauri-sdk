<script lang="ts">
  export let active: boolean = true;
  export let ariaLabel: string = 'Loading Spinner';
</script>

<div class="loading-spinner" role="status" aria-label={ariaLabel} aria-hidden={!active}>
  {#if active}
    <div class="spinner"></div>
  {/if}
</div>

<style lang="css">
  @import './LoadingSpinner.css';
</style>