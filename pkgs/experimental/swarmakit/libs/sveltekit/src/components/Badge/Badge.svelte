<script lang="ts">
  export let type: 'default' | 'notification' | 'status' = 'default';
  export let label: string = '';
  export let ariaLabel: string = 'Badge';

  $: className = `badge ${type}`;
</script>

<span class={className} role="status" aria-label={ariaLabel}>
  {label}
</span>

<style lang="css">
  @import './Badge.css';
</style>