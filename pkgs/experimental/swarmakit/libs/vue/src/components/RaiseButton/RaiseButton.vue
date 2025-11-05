<template>
  <button class="raise-button" :disabled="disabled" aria-label="Raise Bet">
    Raise
  </button>
</template>

<script lang="ts">
import { defineComponent } from 'vue';

export default defineComponent({
  name: 'RaiseButton',
  props: {
    disabled: {
      type: Boolean,
      default: false,
    },
  },
});
</script>

<style scoped lang="css">
.raise-button {
  padding: var(--button-padding);
  font-size: var(--button-font-size);
  background-color: var(--raise-button-bg-color);
  color: var(--button-text-color);
  border: none;
  border-radius: var(--button-border-radius);
  cursor: pointer;
  transition: background-color 0.3s, transform 0.1s;
}

.raise-button:hover:not(:disabled) {
  background-color: var(--raise-button-hover-bg-color);
}

.raise-button:disabled {
  background-color: var(--button-disabled-bg-color);
  cursor: not-allowed;
}

.raise-button:active:not(:disabled) {
  transform: scale(0.95);
}
</style>