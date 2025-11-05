<script lang="ts">
  export let color: string = '#000000';
  export let disabled: boolean = false;

  function handleChange(event: Event) {
    color = (event.target as HTMLInputElement).value;
  }
</script>

<div class="color-picker-container">
  <input
    type="color"
    bind:value={color}
    disabled={disabled}
    aria-label="Color Picker"
    aria-disabled={disabled}
    on:input={handleChange}
  />
  <span class="color-value">{color}</span>
</div>

<style lang="css">
  @import './ColorPicker.css';
</style>