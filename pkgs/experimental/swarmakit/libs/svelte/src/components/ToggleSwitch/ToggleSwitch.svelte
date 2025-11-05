<script lang="ts">
  export let checked: boolean = false;
  export let disabled: boolean = false;

  function toggle() {
    if (disabled) {
      checked = !checked;
    }
  }
</script>

<label class="toggle-switch">
  <input
    type="checkbox"
    bind:checked={checked}
    on:change={toggle}
    disabled={disabled}
    aria-checked={checked}
    aria-disabled={disabled}
    role="switch"
  />
  <span class="slider"></span>
</label>

<style lang="css">
  @import './ToggleSwitch.css';
</style>