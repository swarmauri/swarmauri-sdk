<script lang="ts">
  export let count: number = 0;
  export let maxCount: number = 99;
  export let ariaLabel: string = 'Badge with Count';

  $: displayCount = count > maxCount ? `${maxCount}+` : count.toString();
  $: className = count === 0 ? 'badge zero' : 'badge active';
</script>

<span class={className} role="status" aria-label={ariaLabel}>
  {displayCount}
</span>

<style lang="css">
  @import './BadgeWithCounts.css';
</style>