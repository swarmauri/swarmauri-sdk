<script lang="ts">
  export let message: string = '';
  export let type: 'success' | 'error' | 'warning' | 'info' = 'info';
  export let visible: boolean = true;

  const types = {
    success: 'toast--success',
    error: 'toast--error',
    warning: 'toast--warning',
    info: 'toast--info'
  };

  function dismiss() {
    visible = false;
  }
</script>

{#if visible}
  <div class={`toast ${types[type]}`} role="alert" aria-live="assertive" aria-atomic="true">
    <p>{message}</p>
    <button on:click={dismiss} aria-label="Dismiss notification">✖</button>
  </div>
{/if}

<style lang="css">
  @import './Toast.css';
</style>