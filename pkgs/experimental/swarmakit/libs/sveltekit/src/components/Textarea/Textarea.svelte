<script lang="ts">
  export let value: string = '';
  export let disabled: boolean = false;

  function handleInput(event: Event) {
    value = (event.target as HTMLTextAreaElement).value;
  }
</script>

<textarea
  class="textarea"
  bind:value={value}
  on:input={handleInput}
  disabled={disabled}
  aria-label="Textarea"
></textarea>

<style lang="css">
  @import './Textarea.css';
</style>