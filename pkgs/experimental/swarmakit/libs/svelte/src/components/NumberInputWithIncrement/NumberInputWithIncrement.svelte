<script lang="ts">
  export let value: number = 0;
  export let min: number = -Infinity;
  export let max: number = Infinity;
  export let step: number = 1;
  export let disabled: boolean = false;

  function increment() {
    if (!disabled && value < max) {
      value += step;
    }
  }

  function decrement() {
    if (!disabled && value > min) {
      value -= step;
    }
  }
</script>

<div class="number-input" aria-label="Number Input with Increment">
  <button class="decrement" on:click={decrement} disabled={disabled || value <= min} aria-label="Decrement">-</button>
  <input
    type="number"
    bind:value
    min={min}
    max={max}
    step={step}
    disabled={disabled}
    aria-disabled={disabled}
    aria-valuemin={min}
    aria-valuemax={max}
    aria-valuenow={value}
  />
  <button class="increment" on:click={increment} disabled={disabled || value >= max} aria-label="Increment">+</button>
</div>

<style lang="css">
  @import './NumberInputWithIncrement.css';
</style>