<script lang="ts">
  export let state: 'loading' | 'success' | 'error' = 'loading';

  $: className = `activity-indicator ${state}`;
</script>

<div class={className} role="status" aria-live="polite">
  {#if state === 'loading'}
    <span>Loading...</span>
  {:else if state === 'success'}
    <span>Success!</span>
  {:else if state === 'error'}
    <span>Error occurred!</span>
  {/if}
</div>

<style lang="css">
  @import './ActivityIndicators.css';
</style>