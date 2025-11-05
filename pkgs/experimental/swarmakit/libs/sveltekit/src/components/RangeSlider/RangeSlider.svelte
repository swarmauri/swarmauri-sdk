<script lang="ts">
  export let min: number = 0;
  export let max: number = 100;
  export let value: number = 50;
  export let disabled: boolean = false;
  export let label: string = '';
  export let labelPosition: 'left' | 'center' | 'right' = 'right';

  function handleInput(event: Event) {
    value = (event.target as HTMLInputElement).valueAsNumber;
  }
</script>

<div class="range-slider" aria-disabled={disabled} style={`justify-content: ${labelPosition}`}>
  {#if labelPosition === 'left'}
    <label for="range-slider-input">{label}</label>
  {/if}
  <input
    id="range-slider-input"
    type="range"
    min={min}
    max={max}
    value={value}
    disabled={disabled}
    on:input={handleInput}
    aria-valuemin={min}
    aria-valuemax={max}
    aria-valuenow={value}
    aria-label={label}
  />
  {#if labelPosition === 'center'}
    <label for="range-slider-input">{label}</label>
  {/if}
  {#if labelPosition === 'right'}
    <label for="range-slider-input">{label}</label>
  {/if}
</div>

<style lang="css">
  @import './RangeSlider.css';
</style>