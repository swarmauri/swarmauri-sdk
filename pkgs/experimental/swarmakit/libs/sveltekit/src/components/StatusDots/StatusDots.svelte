<script lang="ts">
  export let status: 'online' | 'offline' | 'busy' | 'idle' = 'offline';
  export let ariaLabel: string = 'Status Indicator';
</script>

<div
  class="status-dots"
  role="status"
  aria-label={ariaLabel}
  data-status={status}
>
  <div class="dot"></div>
</div>

<style lang="css">
  @import './StatusDots.css';
</style>