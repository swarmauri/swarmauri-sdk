<script lang="ts">
  export let label: string;
  export let type: 'primary' | 'secondary' = 'primary';
  export let disabled: boolean = false;
  export let ariaLabel: string;
  export let onClick: () => void;
</script>

<button
  class={`button ${type}`}
  on:click={onClick}
  disabled={disabled}
  aria-label={ariaLabel}
>
  {label}
</button>

<style lang="css">
  @import './Button.css';
</style>