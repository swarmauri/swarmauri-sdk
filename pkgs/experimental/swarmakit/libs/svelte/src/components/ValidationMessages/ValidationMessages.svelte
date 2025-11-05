<script lang="ts">
  export let message: string = '';
  export let type: 'success' | 'error' | 'warning' = 'success';

  $: className = `validation-message ${type}`;
</script>

<div class={className} role="alert" aria-live="polite">
  {message}
</div>

<style lang="css">
  @import './ValidationMessages.css';
</style>