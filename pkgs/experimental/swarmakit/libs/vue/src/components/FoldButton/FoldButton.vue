<template>
  <button class="fold-button" :disabled="disabled" aria-label="Fold Hand">
    Fold
  </button>
</template>

<script lang="ts">
import { defineComponent } from 'vue';

export default defineComponent({
  name: 'FoldButton',
  props: {
    disabled: {
      type: Boolean,
      default: false,
    },
  },
});
</script>

<style scoped lang="css">
.fold-button {
  padding: var(--button-padding);
  font-size: var(--button-font-size);
  background-color: var(--button-bg-color);
  color: var(--button-text-color);
  border: none;
  border-radius: var(--button-border-radius);
  cursor: pointer;
  transition: background-color 0.3s, transform 0.1s;
}

.fold-button:hover:not(:disabled) {
  background-color: var(--button-hover-bg-color);
}

.fold-button:disabled {
  background-color: var(--button-disabled-bg-color);
  cursor: not-allowed;
}

.fold-button:active:not(:disabled) {
  transform: scale(0.95);
}
</style>