<script lang="ts">
  export let icon: string;
  export let disabled: boolean = false;
  export let ariaLabel: string;
  export let onClick: () => void;
</script>

<button
  class="icon-button"
  on:click={onClick}
  disabled={disabled}
  aria-label={ariaLabel}
>
  <img src={icon} alt={ariaLabel} />
</button>

<style lang="css">
  @import './IconButton.css';
</style>