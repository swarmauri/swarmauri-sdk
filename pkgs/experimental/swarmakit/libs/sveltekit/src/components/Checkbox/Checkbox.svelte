<script lang="ts">
  export let label: string;
  export let checked: boolean = false;
  export let disabled: boolean = false;

  function toggleCheck() {
    if (!disabled) {
      checked = !checked;
    }
  }
</script>

<div class="checkbox-container">
  <input
    type="checkbox"
    bind:checked
    disabled={disabled}
    id="checkbox"
    aria-checked={checked}
    aria-disabled={disabled}
    on:change={toggleCheck}
  />
  <label for="checkbox">{label}</label>
</div>

<style lang="css">
  @import './Checkbox.css';
</style>