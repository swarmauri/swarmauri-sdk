<template>
  <button class="call-button" :disabled="disabled" aria-label="Call Bet">
    Call
  </button>
</template>

<script lang="ts">
import { defineComponent } from 'vue';

export default defineComponent({
  name: 'CallButton',
  props: {
    disabled: {
      type: Boolean,
      default: false,
    },
  },
});
</script>

<style scoped lang="css">
.call-button {
  padding: var(--button-padding);
  font-size: var(--button-font-size);
  background-color: var(--button-bg-color);
  color: var(--button-text-color);
  border: none;
  border-radius: var(--button-border-radius);
  cursor: pointer;
  transition: background-color 0.3s, transform 0.1s;
}

.call-button:hover:not(:disabled) {
  background-color: var(--button-hover-bg-color);
}

.call-button:disabled {
  background-color: var(--button-disabled-bg-color);
  cursor: not-allowed;
}

.call-button:active:not(:disabled) {
  transform: scale(0.95);
}
</style>