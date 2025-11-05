<script lang="ts">
  export let level: number = 0;
  export let isCharging: boolean = false;
  export let ariaLabel: string = 'Battery Level Indicator';

  $: levelClass = level > 80 ? 'full' : level > 20 ? 'low' : 'critical';
  $: chargingClass = isCharging ? 'charging' : '';
</script>

<div class={`battery ${levelClass} ${chargingClass}`} role="status" aria-label={ariaLabel}>
  <div class="level" style="width: {level}%"></div>
</div>

<style lang="css">
  @import './BatteryLevelIndicator.css';
</style>