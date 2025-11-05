<script lang="ts">
  export let strength: 'full' | 'weak' | 'none' = 'none';
  export let ariaLabel: string = 'Signal Strength Indicator';
</script>

<div
  class="signal-strength-indicator"
  role="status"
  aria-label={ariaLabel}
  data-strength={strength}
>
  <div class="bar bar1"></div>
  <div class="bar bar2"></div>
  <div class="bar bar3"></div>
  <div class="bar bar4"></div>
  <div class="bar bar5"></div>
</div>

<style lang="css">
  @import './SignalStrengthIndicator.css';
</style>