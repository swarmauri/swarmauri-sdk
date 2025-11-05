<script lang="ts">
  export let value: number = 50;
  export let min: number = 0;
  export let max: number = 100;
  export let isDisabled: boolean = false;
  export let step: number = 1;
</script>

<input
  type="range"
  class="slider"
  min={min}
  max={max}
  step={step}
  value={value}
  disabled={isDisabled}
  aria-valuemin={min}
  aria-valuemax={max}
  aria-valuenow={value}
  aria-label="Slider"
  tabindex="0"
/>

<style lang="css">
  @import './Slider.css';
</style>